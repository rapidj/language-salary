# language-salary
Estimation of average salary in Moscow by programming languages using data from [HeadHunter](https://hh.ru/) and 
[SuperJob](https://superjob.ru/).  

# How to start

Python3 should be already installed. Then use pip to install dependencies:

```bash
pip install -r requirements.txt
```

### Environment variables

- SJ_LOGIN <- SuperJob login
- SJ_PASSWORD <- SuperJob password
- SJ_CLIENT_ID <- get your application 'ID' 
- SJ_CLIENT_SECRET <- get your application 'Secret key'

### How to get

1. Create an account on [SuperJob](https://api.superjob.ru/)

2. Register your application and find your application ID and Secret key in your account section 
   ["Your Application/Access parameters"](https://api.superjob.ru/info/) 

### Run

Run the script main.py:

`python main.py`.

You will see the result tables in the console.