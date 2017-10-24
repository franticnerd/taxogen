Generate json from TaxonGen output txt file

```
python3 taxon2json.py -input ./sample_taxonomy.txt
```

To start visualization the results, you can directly open tree.html in **Safari** or **FireFox**.
If you want to view the results in chrome, you need to first type in the following command and view on **0.0.0.0:8002**.

```
$ python -m SimpleHTTPServer 8002 (if python2)
$ python -m http.server 8002 (if python3)
```

