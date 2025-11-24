To get started, set your OPENAI_API_KEY environment variable, or other required keys for the providers you selected.

Next, edit promptfooconfig.yaml.

Then run:
```
promptfoo eval
```

To get results from a specific file:
    - promptfooconfig-factual.yaml 
    - promptfooconfig-reasoning.yaml
    - promptfooconfig-safety.yaml

From the init directory run:
```
promptfoo eval -c <filename.yaml> -o results.json 

After you have a results.json file open the analyze_tokens.py file and click the run file button to pull the latests results from the eval to give you a token analysis.


Afterwards, you can view the results by running `promptfoo view`
