# Dosya: users/serializers.py
from rest_framework import serializers
from .models import CustomUser
from connections.models import Like
from geonamescache import GeonamesCache
import pytz
from datetime import datetime
from flatlib import const
from flatlib.datetime import Datetime as FlatlibDatetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart

def get_astro_data(user):
    try:
        gc = GeonamesCache()
        cities = gc.search_cities(user.dogum_yeri, case_sensitive=False)
        if not cities: raise ValueError(f"City '{user.dogum_yeri}' not found.")
        city_data = cities[0]
        pos = GeoPos(city_data['latitude'], city_data['longitude'])
        local_tz = pytz.timezone(city_data['timezone'])
        local_dt = local_tz.localize(datetime.combine(user.dogum_tarihi, user.dogum_saati))
        date = FlatlibDatetime(local_dt.strftime('%Y/%m/%d'), local_dt.strftime('%H:%M'), f'{local_dt.utcoffset().total_seconds() / 3600:+0.0f}:00')
        chart = Chart(date, pos)
        sun, moon, asc = chart.get(const.SUN), chart.get(const.MOON), chart.get(const.ASC)
        return {"gunes_burcu": sun.sign, "ay_burcu": moon.sign, "yukselen_burc": asc.sign}
    except Exception as e:
        print(f"ASTROLOJİ HESAPLAMA HATASI: {e}")
        return {"gunes_burcu": "Hata", "ay_burcu": "Hata", "yukselen_burc": "Hata"}

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'dogum_tarihi', 'dogum_saati', 'dogum_yeri', 'bio')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
        user.dogum_tarihi, user.dogum_saati, user.dogum_yeri, user.bio = validated_data.get('dogum_tarihi'), validated_data.get('dogum_saati'), validated_data.get('dogum_yeri'), validated_data.get('bio', '')
        astro_data = get_astro_data(user)
        if astro_data:
            user.gunes_burcu, user.ay_burcu, user.yukselen_burc = astro_data.get('gunes_burcu', 'Hata'), astro_data.get('ay_burcu', 'Hata'), astro_data.get('yukselen_burc', 'Hata')
        user.save()
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'bio', 'dogum_tarihi', 'dogum_saati', 'dogum_yeri', 'gunes_burcu', 'ay_burcu', 'yukselen_burc', 'is_liked')
        extra_kwargs = {'email': {'read_only': True},'gunes_burcu': {'read_only': True},'ay_burcu': {'read_only': True},'yukselen_burc': {'read_only': True}}
    def get_is_liked(self, obj):
        user = self.context.get('request').user
        return user and user.is_authenticated and Like.objects.filter(from_user=user, to_user=obj).exists()

class UserListSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'bio', 'gunes_burcu', 'ay_burcu', 'yukselen_burc', 'is_liked')
    def get_is_liked(self, obj):
        user = self.context.get('request').user
        return user and user.is_authenticated and Like.objects.filter(from_user=user, to_user=obj).exists()