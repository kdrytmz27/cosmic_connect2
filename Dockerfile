# Adım 1: Temel olarak resmi Python 3.11 imajını kullan
FROM python:3.11-slim

# Adım 2: Konteyner içindeki çalışma ortamını ayarla
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Adım 3: Gerekli paketleri kurmadan önce, derleme için gerekli olan
# sistem araçlarını kuruyoruz. (YENİ EKLENEN ADIM)
# Bu satır, 'gcc' gibi derleyicileri kurar.
RUN apt-get update && apt-get install -y build-essential

# Adım 4: Gerekli Python paketlerini kur
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Adım 5: Proje dosyalarını konteynerin içine kopyala
COPY . .

# Adım 6: Sunucunun çalışacağı portu dışarıya aç
EXPOSE 8000

# Adım 7: Konteyner çalıştığında otomatik olarak Django sunucusunu başlat
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]