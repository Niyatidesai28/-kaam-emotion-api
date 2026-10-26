# Findings

| ID / severity | Baseline evidence / reproduction | Result / repair |
|---|---|---|
| K1 High, blocker | main.py:13,20–21; run uvicorn in fresh clone | missing model/kaam_config.json prevents startup; model artifacts also absent; cannot safely fabricate repair |
| K2 Medium | main.py:125–133; compare single whitespace request to batch [whitespace] | single returned neutral sentinel; batch ran classifier; unify blank check in predict_emotion; regression |
| K3 Medium | main.py:11; start from another directory | ./model resolved against shell CWD; make path relative to __file__; path regression |
| K4 Medium | main.py:133; submit 11 texts | only ten results, no rejection/notice; preserve existing contract, defer API policy change |
| K5 High | main.py:45,74 and request schema | arbitrary text/batch body length leads to unbounded tokenization/inference work | document; set agreed request/token/concurrency budgets before deployment |
| K6 Medium | main.py:82–85 | 101/102/0 token IDs assume BERT conventions | verify actual tokenizer before changing; missing artifacts block compatibility proof |
| K7 Medium | main.py:101 | equal chunk averaging and overlap reweight portions of long texts | document model-quality concern; needs labeled evaluation, not speculative scoring rewrite |
| K8 Medium | main.py:33,41 | wildcard CORS, no auth; user_id unused | cannot claim identity/session isolation; defer ownership model |
| K9 High | requirements.txt | old framework/model-library versions | advisory scan captured; compatibility-sensitive upgrades deferred |
| K10 Low | main.py:119–121 | static health/model label | no true readiness endpoint; import-time load blocks health during failures |

No quality metric, training data, calibration study, language coverage or fairness evaluation
was found. Those are evidence gaps, not proof the unseen model is inaccurate. There are no
frontend bugs to reproduce because its source is absent. Unit fixtures are not a substitute
for valid artifact loading or semantic inference tests.
