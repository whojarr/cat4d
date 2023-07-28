# Cat4d 

Testing 4d and s3 web generation with the aid of openai

## Requirements

* poetry
* yarn

## Local Setup

```shell
yarn install
poetry install
```

```shell
cp example.env .env
```

update .env

### Startup

```shell
poetry shell
sls wsgi serve
```

or

```shell
poetry shell
sls wsgi serve --aws-profile {myprofile}
```

## Deploy

```shell
sls deploy --aws-profile {myprofile}
```
