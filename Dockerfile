FROM python:3.10-slim
WORKDIR .
COPY requirements.txt .
ENV env .env
RUN pip install -r requirements.txt --no-cache-dir
COPY . vk_geo_parser
CMD ["python3", "vk_geo_parser/manage_queries.py", "3"]