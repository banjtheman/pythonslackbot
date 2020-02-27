# curl localhost:9000/run_code?code=print\(\"hello\"\)



# curl localhost:9000/run_code?code=n\=5



# curl localhost:9000/run_code?code=df\=pd.read_csv\(\"sample.csv\"\)


# curl localhost:9000/run_code?code=df

curl localhost:9000/run_code?code=df[\'x\'].value_counts\(\).to_json\(\)
