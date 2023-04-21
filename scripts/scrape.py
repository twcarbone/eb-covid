import argparse
import datetime as dt
import logging
import re

import bs4
import requests

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

    return parser.parse_args()


def logging_setup(level):
    logging.getLogger(__name__)
    logging.basicConfig(
        format="[%(asctime)s - %(levelname)s] %(message)s",
        # datefmt="%d/%b/%Y %H:%M:%S",
        datefmt="%c",
        level=level,
        force=True,
    )


def grep(regex, s, item):
    m = re.search(regex, s)
    if m is None:
        logging.warning(f"Failed to resolve {item} from '{s}'")
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
        logging.warning(f"Failed to resolve {item} from '{s}'")
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
        "id": grep_num("^#(.+):.*$", text, "num"),
        "facility": grep(": Employee from (.+) facility", text, "facility"),
        "dept": grep("Dept. (\w+),", text, "dept"),
        "bldg": grep("Bldg. (.+),", text, "bldg"),
        "post_day": post_day,
        "last_day": grep_date("last day of work on {} and tested", text, "last_day", post_day.year),
        "test_day": grep_date("tested on {}\.?", text, "test_day", post_day.year),
    }


def get_soup():
    logging.info("Getting HTML...")
    page = requests.get(url="https://eblanding.com/covid-19-case-report-summary/")
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    logging.info("Done.")
    return soup


def parse_html(args) -> list[dict]:
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
        logging.info(f"Getting cases for {post_day}...")

        # Each case reported on the given day is contained in an <li> tag
        for li in item.next_sibling.next_sibling.find_all("li"):
            logging.debug(li)

            # <h3> of the <li> contains the entire case text
            h3 = li.find("h3")

            if h3 is not None:
                text = h3.get_text()
            else:
                logging.warning(f"No case data for '{li.get_text()}'")
                continue

            cases.append(parse_case(text=text, post_day=post_day))

    return cases


def main():
    args = parse_args()
    logging_setup(args.verbosity)
    return parse_html(args)


if __name__ == "__main__":
    cases = main()
