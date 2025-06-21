# Dosya: connections/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .models import Like
from users.models import CustomUser
from users.serializers import UserListSerializer

# Gerekli astroloji kütüphaneleri
from geonamescache import GeonamesCache
import pytz
from datetime import datetime
from flatlib import const
from flatlib.datetime import Datetime as FlatlibDatetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.aspects import getAspect

def get_chart_from_user(user):
    gc = GeonamesCache()
    cities = gc.search_cities(user.dogum_yeri, case_sensitive=False)
    if not cities: raise ValueError(f"City '{user.dogum_yeri}' not found for {user.username}")
    city_data = cities[0]
    pos = GeoPos(city_data['latitude'], city_data['longitude'])
    local_tz = pytz.timezone(city_data['timezone'])
    local_dt = local_tz.localize(datetime.combine(user.dogum_tarihi, user.dogum_saati))
    date = FlatlibDatetime(local_dt.strftime('%Y/%m/%d'), local_dt.strftime('%H:%M'), f'{local_dt.utcoffset().total_seconds() / 3600:+0.0f}:00')
    return Chart(date, pos)

def calculate_compatibility(user1, user2):
    try:
        chart1, chart2 = get_chart_from_user(user1), get_chart_from_user(user2)
        score = 50 
        major_planets = [const.SUN, const.MOON, const.VENUS, const.MARS, const.SATURN]
        aspect_scores = {const.CONJUNCTION: 10, const.OPPOSITION: -5, const.SQUARE: -4, const.TRINE: 8, const.SEXTILE: 6}
        harmonious_aspects, challenging_aspects = [], []
        for p1_id in major_planets:
            p1 = chart1.get(p1_id)
            for p2_id in major_planets:
                p2 = chart2.get(p2_id)
                aspect = getAspect(p1, p2, const.MAJOR_ASPECTS)
                if aspect:
                    strength = (8 - aspect.orb) / 8
                    if aspect.type in aspect_scores:
                        score += aspect_scores[aspect.type] * strength
                        desc = f"Sizin {p1.id}'ınız ile onun {p2.id}'ı arasında {aspect.type} açısı var."
                        if aspect_scores[aspect.type] > 0: harmonious_aspects.append(desc)
                        else: challenging_aspects.append(desc)
        return {"score": int(max(0, min(100, score))), "harmonious": harmonious_aspects, "challenging": challenging_aspects}
    except Exception as e:
        print(f"Compatibility calculation error: {e}")
        return {"error": str(e)}

class CompatibilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        try:
            user1, user2 = self.request.user, CustomUser.objects.get(pk=pk)
            required_fields = ['dogum_tarihi', 'dogum_saati', 'dogum_yeri']
            for field in required_fields:
                if not getattr(user1, field): return Response({"error": f"Giriş yapmış kullanıcının '{field}' bilgisi eksik."}, status=status.HTTP_400_BAD_REQUEST)
                if not getattr(user2, field): return Response({"error": f"Bakılan kullanıcının (ID: {user2.id}) '{field}' bilgisi eksik."}, status=status.HTTP_400_BAD_REQUEST)
            result = calculate_compatibility(user1, user2)
            return Response(result) if "error" not in result else Response(result, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Uyum hesaplanırken bir hata oluştu: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LikeUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        try:
            to_user = CustomUser.objects.get(pk=pk)
            from_user = request.user
            if from_user == to_user:
                return Response({"error": "Kendinizi beğenemezsiniz."}, status=status.HTTP_400_BAD_REQUEST)
            like, created = Like.objects.get_or_create(from_user=from_user, to_user=to_user)
            if not created: return Response({"status": "already_liked"}, status=status.HTTP_200_OK)
            is_match = Like.objects.filter(from_user=to_user, to_user=from_user).exists()
            if is_match: return Response({"status": "match_created"}, status=status.HTTP_201_CREATED)
            return Response({"status": "like_created"}, status=status.HTTP_201_CREATED)
        except CustomUser.DoesNotExist:
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

class MatchListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        i_like = set(Like.objects.filter(from_user=user).values_list('to_user_id', flat=True))
        likes_me = set(Like.objects.filter(to_user=user).values_list('from_user_id', flat=True))
        match_ids = list(i_like.intersection(likes_me))
        return CustomUser.objects.filter(id__in=match_ids)
    def get_serializer_context(self):
        return {'request': self.request}