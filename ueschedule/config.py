import argparse


class Config():
    cal_url = "https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz/calendarid_{uid}.ics"
    cal_url_filter = "?dataod={start}&datado={end}"

    def __init__(self):
        # TODO save/read the uid from config file
        self.opts = self.parse_args()

    def parse_args(self):
        parser = argparse.ArgumentParser(description='UE Schedule Tool.')
        parser.add_argument('uid', type=int, help='User ID')
        parser.add_argument('--start', '-s', help="Start date")
        parser.add_argument('--end', '-e', help="End date")

        return parser.parse_args()

    @property
    def schedule_url(self):
        url = self.cal_url.format(uid=self.opts.uid)

        if self.opts.start and self.opts.end:
            url += self.cal_url_filter.format(start=self.opts.start, end=self.opts.end)

        return url
