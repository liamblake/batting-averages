from csv import writer

from bs4 import BeautifulSoup, SoupStrainer
from requests import get
from tqdm import tqdm


def get_batting_averages(baseurl, outdir):
    page = get(baseurl)

    # Get the total number of pages
    page_no_soup = BeautifulSoup(
        page.text,
        "html.parser",
        parse_only=SoupStrainer(
            "td", attrs={"class": "left", "style": "vertical-align:middle"}
        ),
    )
    no_pages = int(page_no_soup.find_all("b", limit=2)[1].text)

    csv_rows = []
    for i in tqdm(range(no_pages)):
        page = get(f"{baseurl};page={i+1}")
        rows = BeautifulSoup(
            page.text,
            "html.parser",
            parse_only=SoupStrainer("tr", attrs={"class": "data1"}),
        )
        for r in rows:
            tds = r.find_all("td")
            name_team_split = tds[0].text.split(" (")
            if len(name_team_split) == 3:
                # Occurs with some duplicate names - e.g. Abdul Malik (1).
                del name_team_split[1]

            csv_rows.append(
                [name_team_split[0], name_team_split[1][:-1]]
                + [tds[j].text for j in range(1, 11)]
            )

    # Open the output CSV file
    with open(outdir, "w") as file:
        wr = writer(file)
        # Header of CSV
        wr.writerow(
            [
                "name",
                "team",
                "span",
                "mat",
                "inns",
                "no",
                "runs",
                "hs",
                "ave",
                "100",
                "50",
                "0",
            ]
        )

        # Content
        wr.writerows(csv_rows)


if __name__ == "__main__":
    outdir = "batting_averages.csv"
    get_batting_averages(
        "https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;orderby=player;size=200;template=results;type=batting",
        outdir,
    )
