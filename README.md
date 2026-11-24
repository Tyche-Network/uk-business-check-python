# UK business check API for Python

> **UK VAT: source unavailable for now.** Company, EORI and charity checks are live. UK VAT checks wait for HMRC production access: until then `vat` is `null`, `meta.sources.hmrc` is `unavailable` and `vat()` returns 503 (not counted). Get a free key at https://api.tychelabs.net/signup

Check a UK company in one call. You get Companies House status, age, overdue flags and filings. HMRC validates the VAT number, the Charity Commission gives charity status, and plain risk flags sit on top. Officer and PSC data come back as counts only. Standard library only, Python 3.9+.

Free plan with 50 checks a month: https://api.tychelabs.net/business. Docs: https://api.tychelabs.net/docs/business

```sh
pip install git+https://github.com/Tyche-Network/uk-business-check-python
```

```python
from uk_business_check import BusinessCheck

api = BusinessCheck()  # reads TYCHE_API_KEY
c = api.check("16716814", vat="GB553557881")["data"]

print(c["company"]["name"], c["company"]["status"], c["company"]["ageYears"])
print("VAT valid:", (c["vat"] or {}).get("valid"))  # None until HMRC is connected
for f in c["flags"]:
    print(f["severity"], f["message"])

matches = api.search("example trading")

# UK and EU EORI numbers, on their own or in check(..., eori=...)
eori = api.eori("GB123456789000")["data"]["data"]["items"]
```

A `tl_test_` key returns sandbox data and is not metered. `api.watch("16716814", url)` sends signed events when status, overdue flags or risk change. Check each one with `verify_webhook`.

Company data comes from the Companies House public register. VAT checks use HMRC. Charity data is from the Charity Commission (Open Government Licence v3.0). Not affiliated with or endorsed by Companies House, HMRC or the Charity Commission.

MIT licence. Made by [Tyche Labs](https://www.tychelabs.net).
