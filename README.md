# UK business check API for Python

> **Coming soon.** The business check API opens when Companies House and HMRC VAT are both connected. Keys and plans are not available yet. Vehicle keys are available now at https://api.tychelabs.net/signup?product=vehicle

Check a UK company in one call. You get Companies House status, age, overdue flags and filings. HMRC validates the VAT number, the Charity Commission gives charity status, and plain risk flags sit on top. Officer and PSC data come back as counts only. Standard library only, Python 3.9+.

Free plan with 50 checks a month when it opens: https://api.tychelabs.net/business-api. Docs: https://api.tychelabs.net/docs/business

```sh
pip install git+https://github.com/Tyche-Network/uk-business-check-python
```

```python
from uk_business_check import BusinessCheck

api = BusinessCheck()  # reads TYCHE_API_KEY
c = api.check("16716814", vat="GB553557881")["data"]

print(c["company"]["name"], c["company"]["status"], c["company"]["ageYears"])
print("VAT valid:", c["vat"]["valid"])
for f in c["flags"]:
    print(f["severity"], f["message"])

matches = api.search("example trading")["data"]["items"]
```

A `tl_test_` key returns sandbox data and is not metered. `api.watch("16716814", url)` sends signed events when status, overdue flags or risk change. Check each one with `verify_webhook`.

Company data comes from the Companies House public register. VAT checks use HMRC. Charity data is from the Charity Commission (Open Government Licence v3.0). Not affiliated with or endorsed by Companies House, HMRC or the Charity Commission.

MIT licence. Made by [Tyche Labs](https://www.tychelabs.net).
