# python image 
FROM python:3.11.9 


# Working Docker Directory 
WORKDIR /app 


# Copy requirements.txt so docker first run this and dont run again and again if any change in the file
COPY requirements.txt  .


# Install CPU-only PyTorch first
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu


# Install Requirments 
RUN  pip install -r requirements.txt 


COPY all-mpnet-base-v2-local /app/all-mpnet-base-v2-local


# Copy whole project 
COPY . . 


# Run FastApi App 
CMD ["uvicorn", "mainb:app", "--host", "0.0.0.0", "--port", "8001"]