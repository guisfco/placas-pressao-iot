# placas-pressao-iot
Trabalho final para a disciplina de Internet das Coisas - Unisinos 2023

## Execução
### Para executar com Docker
```shell
docker run -p 3000:3000 guisfco/placas-pressao-iot
```
Ou
```shell
docker-compose up -d
```

### Para executar manualmente
```shell
pip install -r requirements.txt
python -m flask --app main run --port=3000
```

## Acesso
Link: http://localhost:3000/