import argparse
import datetime as dt
import re

import bs4
import requests

import app.models as db
import log

logger = log.logging.getLogger("EBCovid.scrape")

URL = "https://eblanding.com/covid-19-case-report-summary/"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbosity",
        help="Set logging level X (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL). Defaults to 20 (INFO).",
        metavar="X",
        type=int,
        dest="verbosity",
        default=20,
    )
    parser.add_argument(
        "--dbenv",
        help="Insert records to database environment X (dev, test, prod)",
        metavar="X",
        type=str,
        dest="dbenv",
        default=None,
    )

    args = parser.parse_args()

    if args.dbenv is not None and args.dbenv not in ["dev", "test", "prod"]:
        parser.error("--dbenv must be 'dev', 'test', or 'prod'")

    return args


def grep(regex, s, item):
    m = re.search(regex, s)
    if m is None:
        logger.warning(f'Failed to resolve {item} from "{s}"')
        return None
    else:
        return m.group(1)


def grep_date(regex, s, item, year) -> dt.date:
    """ """
    # Regex for date. Matches 'Janaury 21, 1990', 'January 21 ,1990', 'Janaury 21'. Named
    # capture groups are: month=Janaury, day=21, and year=1990.
    date_regex = "(?P<month>[a-zA-Z]+) (?P<day>\d{1,2})(?:.{1,2}(?P<year>\d{4}))?"
    m = re.search(regex.format(date_regex), s)
    if m is None:
        logger.warning(f'Failed to resolve {item} from "{s}"')
        return None

    groupdict = m.groupdict()
    month = groupdict.get("month")
    day = groupdict.get("day")
    year = groupdict.get("year") or year

    return dt.datetime.strptime(f"{month} {day} {year}", "%B %d %Y").date()


def grep_num(regex, s, item) -> int:
    num = grep(regex, s, item)
    if num is None:
        return None

    return int(num.replace(",", ""))


def parse_case(text, post_day):
    return {
        "id": grep_num("#\s*([\d,]+).*:.*$", text, "num"),
        "facility": grep(":\s*Employee from ([\w\s'()]+)", text, "facility"),
        "dept": grep("Dept.\s*([\d/]+)", text, "dept"),
        "bldg": grep("Bldg. (.+),", text, "bldg"),
        "post_day": post_day,
        "last_day": grep_date("last day of work on {}", text, "last_day", post_day.year),
        "test_day": grep_date("tested on {}\.?", text, "test_day", post_day.year),
    }


def get_soup():
    logger.info("Getting HTML...")
    page = requests.get(url="https://eblanding.com/covid-19-case-report-summary/")
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    logger.info("Done.")
    return soup


def parse_html() -> list[dict]:
    """
    Parse HTML from https://eblanding.com/covid-19-case-report-summary/.

    Return list of `dict`. Each `dict` is:
    ```
    {
        "id": int | None,
        "facility": str | None,
        "dept": str | None,
        "bldg": str | None,
        "post_day" datetime.date | None,
        "last_day" datetime.date | None,
        "test_day" datetime.date | None,
    }
    ```
    """
    soup = get_soup()
    cases = []

    # Each <pre> or <p> tag denotes a new day of case reporting
    # e.g. 'Posted on October 17, 2020:'
    pre = soup.find("article").find("div").find_all("pre")
    p = soup.find("article").find("div").find_all("p")

    for item in pre + p:
        post_day = grep_date("Posted on {}:?", item.get_text(), "post_day", 1990)
        logger.info(f"Getting cases for {post_day}...")

        # Each case reported on the given day is contained in an <li> tag
        for li in item.next_sibling.next_sibling.find_all("li"):
            logger.debug(li)

            # <h3> of the <li> contains the entire case text
            h3 = li.find("h3")

            if h3 is not None:
                text = h3.get_text()
            else:
                logger.warning(f"No case data for '{li.get_text()}'")
                continue

            cases.append(parse_case(text=text, post_day=post_day))

    return cases


def parse_html2():
    soup = get_soup()
    cases = []
    for text in re.findall("#.*", soup.get_text()):
        # TODO: Posted date is garbage using this method
        cases.append(parse_case(text=text, post_day=dt.date(1900, 1, 1)))
    return cases


def distinct(cases: list[dict], key: str) -> None:
    """
    Return a sorted list of distinct values of *key*. Discards `None` if it is a value.
    """
    set_ = {case[key] for case in cases}
    set_.discard(None)
    return sorted(list(set_))


def to_db(cases: list, dbenv: str):
    """
    Add cases from *cases* to database denoted by environment *dbenv* (dev, test, prod).
    """
    with db.ssn_from_dbenv(dbenv=dbenv) as ssn:
        for case in cases:
            facility = db.Facility(name=case["facility"])
            ssn.add(facility)
            ssn.flush()


def main():
    args = parse_args()
    logger.setLevel(args.verbosity)
    cases = parse_html()
    # TODO: Coerce facilities to proper format
    if args.dbenv is not None:
        to_db(cases, args.dbenv)
    return cases


if __name__ == "__main__":
    cases = main()
