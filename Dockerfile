# Use node image that already includes nodejs and npm
FROM node:18-slim

# Install Python and other dependencies more efficiently
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3-venv \
    python3-full \
    chromium \
    chromium-driver \
    git \
    # Add ODBC dependencies
    gnupg2 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Remove any existing ODBC packages to avoid conflicts
RUN apt-get update && apt-get remove -y --purge \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    odbcinst \
    && apt-get autoremove -y \
    && apt-get clean

# Install Microsoft ODBC Driver 17 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql17 \
    unixodbc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set display port to avoid crash
ENV DISPLAY=:99

# Set working directory in the container
WORKDIR /app

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir pip setuptools wheel
RUN pip install --no-cache-dir -e .

# Copy the current directory contents into the container
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run Chainlit when the container launches
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"] 