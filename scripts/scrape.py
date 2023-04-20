import argparse
import datetime as dt
import re

import bs4
import requests

URL = "https://eblanding.com/covid-19-case-report-summary/"


def parse_args():
    parser = argparse.ArgumentParser()

    return parser.parse_args()


def grep(regex, s, item):
    m = re.search(regex, s)
    if m is not None:
        Warning(f"Failed to resolve {item} from '{s[:20]}...'")
        return None
    else:
        return m.group(1)


def grep_date(regex, s, item, year) -> dt.date:
    date = grep(regex, s, item)
    if date is None:
        return None

    try:
        dt_obj = dt.datetime.strptime(date, "%B %d %Y")
    except ValueError:
        # Cases posted earlier than January 3, 2022 did not report the year in the case
        # text; only the month and day was posted. Need to assign year explicitly.
        dt_obj = dt.datetime.strptime(date, "%B %d").replace(year=year)

    return dt_obj.date()


def grep_num(regex, s, item) -> int:
    num = grep(regex, s, item)
    if num is None:
        return None

    return int(num.replace(",", ""))


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

    page = requests.get(url="https://eblanding.com/covid-19-case-report-summary/")
    soup = bs4.BeautifulSoup(page.content, "html.parser")

    cases = []

    # Each <pre> or <p> tag denotes a new day of case reporting
    # e.g. 'Posted on October 17, 2020:'
    pre = soup.find("article").find("div").find_all("pre")
    p = soup.find("article").find("div").find_all("p")

    for item in pre + p:
        post_day = dt.strptime(item.get_text()[10:-1], "%B %d, %Y").date()

        # Each case reported on the given day is contained in an <li> tag
        for li in item.next_sibling.next_sibling.find_all("li"):
            # <h3> of the <li> contains the entire case text
            text = li.find("h3").get_text()

            cases.append(
                {
                    "id": grep_num("^#(.+):.*$", text, "num"),
                    "facility": grep(": Employee from (.+) facility", text, "facility"),
                    "dept": grep("Dept. (+\w),", text, "dept"),
                    "bldg": grep("Bldg. (.+),", text, "bldg"),
                    "post_day": post_day,
                    "last_day": grep_date("last day of work on (.+) and tested", text, "last_day", post_day.year),
                    "test_day": grep_date("tested on (.+).*$", text, "test_day", post_day.year),
                }
            )

    return cases


def main():
    args = parse_args()
    cases = parse_html(args)


if __name__ == "__main__":
    main()
