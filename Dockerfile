FROM python:3.10.18

# Install Poetry
RUN	python -m pip install --upgrade pip

ENV POETRY_HOME=/opt/poetry
RUN curl --proto "=https" -sSL https://install.python-poetry.org | python3 -
ENV PATH="$PATH:$POETRY_HOME/bin"

RUN echo poetry --version

RUN poetry self update && \
    poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PROJECT_PATH="/app"

WORKDIR ${PROJECT_PATH}

COPY src ./src

# Set workdir and copy files
COPY pyproject.toml .

COPY start.sh .
RUN chmod +x ./start.sh

RUN poetry install --only main

CMD ["./start.sh"]


