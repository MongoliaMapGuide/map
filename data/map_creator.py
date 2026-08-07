import os
import pandas as pd
import folium
from folium.plugins import LocateControl, Search, MarkerCluster, MeasureControl


# 1. МАРКЕР НЭМЭХ ФУНКЦ
def add_markers_by_type(df, groups, search_layer):
    df.columns = df.columns.str.strip()
    df = df.fillna("")
    default_logo = "https://github.com/MongoliaMapGuide/map/blob/main/logo512.png?raw=true"

    for index, row in df.iterrows():
        try:
            lat = float(row.get('Lat', 0))
            long = float(row.get('Long', 0))
            if lat == 0 or long == 0: continue
            p_val = int(float(row.get('Point_type', 1)))

            # Тэмдэгтүүдийг цэвэрлэх
            name_mn = str(row.get('Name_mon', '-')).replace("'", "\\'").strip()
            name_en = str(row.get('Name_eng', '-')).replace("'", "\\'").strip().upper()
            name_kr = str(row.get('Name_kr', '-')).replace("'", "\\'").strip()
            name_jp = str(row.get('Name_jp', '-')).replace("'", "\\'").strip()
            name_cn = str(row.get('Name_cn', '-')).replace("'", "\\'").strip()
            name_ru = str(row.get('Name_ru', '-')).replace("'", "\\'").strip()
            aimag_en = str(row.get('Aimag_name_eng', '-')).strip()
            sum_en = str(row.get('Sum_name_eng', '-')).strip()
            aimag_mn = str(row.get('Aimag_name_mn', aimag_en)).strip()
            photo = str(row.get('Photo_URL', '')).strip()
            phone_val = str(row.get('Phone', '')).strip()
            phone_display = phone_val if phone_val.lower() not in ['nan', 'none', '', '0'] else None
            lat = row.get('Latitude', '0')
            long = row.get('Longitude', '0')
            final_img = photo.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0",
                                                                                              "raw=1") if "http" in photo.lower() else default_logo

            target_grp, icon_name, icon_color = groups.get(p_val, (None, 'leaf', 'gray'))
            if target_grp is None: continue

            # 🌐 Олон хэлний өгөгдөл байхгүй бол англи нэрийг орлуулах хамгаалалт
            kr_title = name_kr if name_kr and name_kr != '-' else name_en
            jp_title = name_jp if name_jp and name_jp != '-' else name_en
            cn_title = name_cn if name_cn and name_cn != '-' else name_en
            ru_title = name_ru if name_ru and name_ru != '-' else name_en

            # 📱 Хэл бүрээр харагдах дэд гарчиг, мэдээллийн хэсэг (Хуучин байсан тугтай хувилбар руу буцаав)
            lang_section_html = f"""
            <div class="pop-lang lang-mn" style="display: block;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇲🇳 {name_mn}</div>
            </div>
            <div class="pop-lang lang-en" style="display: none;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇺🇸 {name_en}</div>
            </div>
            <div class="pop-lang lang-kr" style="display: none;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇰🇷 {kr_title}</div>
            </div>
            <div class="pop-lang lang-jp" style="display: none;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇯🇵 {jp_title}</div>
            </div>
            <div class="pop-lang lang-cn" style="display: none;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇨🇳 {cn_title}</div>
            </div>
            <div class="pop-lang lang-ru" style="display: none;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇷🇺 {ru_title}</div>
            </div>
            """

            # 🎨 1-Р ПОПАП: Фэйсбүүк хуудасны линктэй хувилбар
            lat = row.get('Lat', 0)
            long = row.get('Long', 0)
            fb_raw = row.get('Facebook', '')

            # Хэрэв линк байвал, урд нь http эсвэл https байгаа эсэхийг шалгах
            if fb_raw and not str(fb_raw).startswith(('http://', 'https://')):
                facebook_display = f"https://{fb_raw}"
            else:
                facebook_display = fb_raw
            popup_html = f"""
            <div style="width: 280px; min-width: 280px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.15); display: flex; flex-direction: column;">

                <a href="{final_img}" target="_blank" title="Зургийг томсгож үзэх" style="text-decoration: none; display: block; position: relative; cursor: pointer !important;">
                    <div style="width: 100%; max-height: 225px; overflow: hidden; margin: 0; padding: 0; line-height: 0; background: white; display: flex; align-items: center; justify-content: center;">
                        <img src="{final_img}" 
                             style="width: 100%; height: auto; min-height: 225px; object-fit: cover; object-position: center; display: block; margin: 0; border: none; cursor: pointer !important;" 
                             onerror="this.src='https://via.placeholder.com/280x150?text=No+Image'">
                    </div>
                    <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.6); color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-family: sans-serif; pointer-events: none;">🔍 Томсгох</div>
                </a>

                <div style="padding: 10px 15px 15px 15px; margin-top: -1px; background: white; position: relative; z-index: 2;">
                    <div class="pop-lang lang-mn" style="display: block;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{name_mn}</div>
                    </div>
                    <div class="pop-lang lang-en" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{name_en}</div>
                    </div>
                    <div class="pop-lang lang-kr" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{kr_title}</div>
                    </div>
                    <div class="pop-lang lang-jp" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{jp_title}</div>
                    </div>
                    <div class="pop-lang lang-cn" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{cn_title}</div>
                    </div>
                    <div class="pop-lang lang-ru" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{ru_title}</div>
                    </div>

                    {lang_section_html}

                    <div style="font-size: 11px; color: #444; margin-bottom: 10px; line-height: 1.4; border-top: 1px solid #f5f5f5; padding-top: 10px;">
                        <div style="margin-bottom: 5px;">Location: {sum_en} <b>{aimag_en}</b></div>
                        {f'<div style="margin-bottom: 5px;">Phone: <a href="tel:{phone_display}" style="text-decoration:none; color:#1a73e8; font-weight: 600;">{phone_display}</a></div>' if phone_display else ''}

                        <!-- 🔵 Фэйсбүүк холбоос (Зөвхөн линктэй цэгүүд дээр л гарна) -->
                        {f'<div style="margin-bottom: 5px;">Facebook: <a href="{facebook_display}" target="_blank" style="text-decoration:none; color:#1877F2; font-weight: 600;">Visit Facebook Page</a></div>' if facebook_display else ''}

                        <div style="margin-top: 8px; color: #555; background: #f8f9fa; padding: 8px; border-radius: 6px; border-left: 3px solid #1a73e8;">
                            <b>GPS:</b> 
                            <span style="user-select: all; cursor: pointer; font-family: monospace;">
                            {lat}, {long}
                            </span>
                        </div>
                    </div>

                    <a href="https://www.google.com/maps/search/?api=1&query={lat},{long}" target="_blank" 
                       style="display: block; background: #1a73e8; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px; box-shadow: 0 2px 5px rgba(26,115,232,0.3);">
                        🚀 View on Google Maps
                    </a>
                </div>
            </div>
            """
            icon_html = f'<div style="background-color: {icon_color}; border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.4);"><i class="fa-solid fa-{icon_name}" style="font-size: 14px;"></i></div>'

            # Маркер Кластерт нэмэх
            folium.Marker(
                location=[lat, long],
                popup=folium.Popup(popup_html, max_width=280),
                icon=folium.DivIcon(icon_size=(32, 32), icon_anchor=(16, 16), html=icon_html)
            ).add_to(target_grp)

            # Хайлтад зориулсан
            s_marker = folium.CircleMarker(
                location=[lat, long], radius=5, weight=0, fill_color="rgba(0,0,0,0)", color="rgba(0,0,0,0)",
                popup=folium.Popup(popup_html, max_width=280)
            )
            s_marker.options['search_label'] = f"{name_mn} {name_en}".strip()
            s_marker.add_to(search_layer)
        except:
            continue


# 2. ҮНДСЭН ХЭСЭГ

# === ГАЗРЫН ЗУРАГ ҮҮСГЭХ ЭХЛЭЛ ХЭСЭГ (ЯГ ИНГЭЖ ЗҮҮН ЗАХАД НААЖ БИЧНЭ 🚀) ===
import os
import folium

# 1. САНГУУДЫН ТОХИРУУЛГА БОЛОН ЗАМЫН ХАВТАС
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. ГАЗРЫН ЗУРАГ ҮҮСГЭХ (Суурийг хоосон үлдээж, масштабыг идэвхжүүлнэ)
m = folium.Map(
    location=[47.0, 103.0],
    zoom_start=6,
    tiles=None,
    max_zoom=17,
    control_scale=True
)

# 3. УЛААВТАР ТЕРРЭЙН ДЭВСПЭРИЙГ БОГИНО НЭРТЭЙГЭЭР НЭМЭХ 🚀
folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr='&copy; OpenTopoMap contributors',
    name="OpenTopoMap",  # Зүүн дээд талын цэвэрхэн нэр ✨
    overlay=False,
    control=True
).add_to(m)
# 2. ДАРАА НЬ БУСАД ЭЛЕМЕНТҮҮД ОРНО ✨
# Одоо 153-р мөрөнд байсан код энд байрлах учраас алдаа заахгүй


# 2. ҮНДСЭН ХЭСЭГ (PWA файлуудыг холбосон хувилбар)
m.get_root().header.add_child(folium.Element("""
<title>TravelMap.mn - Mongolia Travel Guide</title>
<meta name="description" content="Interactive travel guide map of Mongolia.">

<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="shortcut icon" href="/favicon.ico">

<link rel="apple-touch-icon" sizes="180x180" href="/logo180.png">
<link rel="manifest" href="/manifest.json">

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1a73e8">

<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    // Ард нь Date.now() залгаснаар хөтөч үргэлж шинэ хувилбар гэж танина
    navigator.serviceWorker.register('/sw.js?v=' + Date.now()).then(function(registration) {
      console.log('Амжилттай бүртгэгдлээ. Хүрээ: ', registration.scope);
    }).catch(function(err) {
      console.log('Бүртгэл амжилтгүй: ', err);
    });
  });
}
</script>

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1a73e8">


        <meta property="og:title" content="TravelMap.mn - Mongolia Travel Guide">
        <meta property="og:description" content="Interactive travel guide map of Mongolia.">
        <meta property="og:image" content="https://travelmap.mn/logo1200x630.png">
        <meta property="og:url" content="https://travelmap.mn">
        <meta property="og:type" content="website">

        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
        <style>
            .leaflet-popup-content-wrapper { padding: 0 !important; border-radius: 12px !important; overflow: hidden !important; width: 280px !important; }
            .leaflet-popup-content { margin: 0 !important; width: 280px !important; }
            .leaflet-popup-close-button { top: 10px !important; right: 10px !important; color: white !important; background: rgba(0,0,0,0.3) !important; border-radius: 50% !important; z-index: 1000; }
            .leaflet-control-layers { margin-bottom: 20px !important; }
        </style>
  <style>
    /* 1. Хамгийн гадна талын Leaflet контейнерийг цэвэрлэх */
    .leaflet-control-layers,
    .leaflet-control-layers-expanded,
    .leaflet-touch .leaflet-control-layers,
    .leaflet-touch .leaflet-control-layers-expanded {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-top: 15px !important;
        margin-right: 15px !important;
        /* Баруун гар тал руу бүхэлд нь шахах */
        display: flex !important;
        justify-content: flex-end !important;
    }

    /* Хоёр баганыг зэрэгцүүлэх хэсэг */
.leaflet-control-layers-list {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
    background: none !important;
    /* --- ЭНЭ ДООРХ УТГЫГ ӨӨРЧЛӨӨРЭЙ --- */
    gap: 10px !important;  /* 15px-ийг ихэсгэж багасгаж болно */
}

    /* 3. Зүүн талын суурь зураг (Таны хэмжээсүүд) */
    .leaflet-control-layers-base {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 10px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        margin-right: 15px !important; /* Бага зэрэг багасгаж зай хэмнэв */
        flex-shrink: 0 !important;
    }

    /* 4. Баруун талын шүүлтүүр (Таны хэмжээсүүд) */
    .leaflet-control-layers-overlays {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 10px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        flex-shrink: 0 !important;
    }

    /* 5. Бичвэрийн хэмжээ (Таны өгсөн 12px) */
    .leaflet-control-layers label {
        font-size: 12px !important;
        margin-bottom: 5px !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
    }

    .leaflet-control-layers input {
        margin-right: 8px !important;
    }

    /* Хэрэв дэлгэц маш жижиг бол (iPhone SE гэх мэт) цонхыг бага зэрэг шахах */
    @media (max-width: 400px) {
        .leaflet-control-layers-base, 
        .leaflet-control-layers-overlays {
            padding: 8px !important;
        }
        .leaflet-control-layers label {
            font-size: 11px !important;
        }
    }
</style>
    """))

# 🎯 ИНГЭЖ ӨӨРЧИЛНӨ (Монгол нэр | Англи нэр болгов):
folium.TileLayer('OpenStreetMap', name='🌐 Гудамжны зураг | Street Map').add_to(m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google',
                 name='🛰️ Хиймэл дагуул | Satellite').add_to(m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google',
                 name='⛰️ Гадаргууны зураг | Terrain Map').add_to(m)

# =========================================================================
# 🎯 1-Р АЛХАМ: КЛАСТЕРЫН НЭРСИЙГ ДУНДУУР НЬ ЗУРААСТАЙ ХОЁР ХЭЛЭЭР ӨГӨХ
# =========================================================================
nature_grp = MarkerCluster(name='Байгалийн үзэсгэлэнт газар | Natural Wonders').add_to(m)
hist_grp = MarkerCluster(name='Түүхэн дурсгалт газар | Historical Sites').add_to(m)
relig_grp = MarkerCluster(name='Сүм хийд, шашны газар | Religious Sites').add_to(m)
camp_grp = MarkerCluster(name='Жуулчны бааз | Tourist Camps').add_to(m)
resort_grp = MarkerCluster(name='Амралтын газар | Resorts').add_to(m)
sanatorium_grp = MarkerCluster(name='Сувилал | Sanatoriums').add_to(m)
child_grp = MarkerCluster(name='Хүүхдийн зуслан | Children\'s Camps').add_to(m)
service_grp = MarkerCluster(name='Зам дагуух үйлчилгээ | Roadside Service').add_to(m)
transport_grp = MarkerCluster(name='Тээвэр, ложистик | Transport').add_to(m)

groups_dict = {
    1: (nature_grp, 'mountain', '#4CAF50'),
    2: (hist_grp, 'landmark', '#2E7D32'),
    3: (relig_grp, 'om', '#FF9800'),
    4: (camp_grp, 'campground', '#673AB7'),
    5: (resort_grp, 'hotel', '#009688'),
    6: (sanatorium_grp, 'briefcase-medical', '#E91E63'),
    7: (child_grp, 'child', '#FF4081'),
    8: (transport_grp, 'plane', '#00838F'),
    9: (transport_grp, 'train', '#0097A7'),
    10: (transport_grp, 'archway', '#00ACC1'),
    11: (service_grp, 'utensils', 'orange'),
    12: (service_grp, 'gas-pump', 'red')
}
search_grp = folium.FeatureGroup(name="Search Layer", control=False).add_to(m)

# Tiles (Terrain-ийг буцааж нэмэв)
folium.TileLayer('OpenStreetMap', name='🌐 Street Map').add_to(m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google',
                 name='🛰️ Satellite').add_to(m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google',
                 name='⛰️ Terrain Map').add_to(m)

# Кластер группүүд
nature_grp = MarkerCluster(name='🏞️ Natural Wonders').add_to(m)
hist_grp = MarkerCluster(name='🏛️ Historical Sites').add_to(m)
relig_grp = MarkerCluster(name='🕉️ Religious Sites').add_to(m)
camp_grp = MarkerCluster(name='⛺ Tourist Camps').add_to(m)
resort_grp = MarkerCluster(name='🏢 Resorts').add_to(m)
sanatorium_grp = MarkerCluster(name='🏥 Sanatoriums').add_to(m)
child_grp = MarkerCluster(name='🧒 Children\'s Camps').add_to(m)
service_grp = MarkerCluster(name='🍽️ Roadside Service').add_to(m)
transport_grp = MarkerCluster(name='✈️ Transport').add_to(m)

groups_dict = {
    1: (nature_grp, 'mountain', '#4CAF50'),
    2: (hist_grp, 'landmark', '#2E7D32'),
    3: (relig_grp, 'om', '#FF9800'),
    4: (camp_grp, 'campground', '#673AB7'),
    5: (resort_grp, 'hotel', '#009688'),
    6: (sanatorium_grp, 'briefcase-medical', '#E91E63'),
    7: (child_grp, 'child', '#FF4081'),
    8: (transport_grp, 'plane', '#00838F'),
    9: (transport_grp, 'train', '#0097A7'),
    10: (transport_grp, 'archway', '#00ACC1'),
    11: (service_grp, 'utensils', 'orange'),
    12: (service_grp, 'gas-pump', 'red')
}
search_grp = folium.FeatureGroup(name="Search Layer", control=False).add_to(m)

# Өгөгдөл унших хэсэг (Таны өмнөх кодын дагуу)
df_all = pd.DataFrame()
for f in ["Tourist_camps_multi.csv", "Nature_His_multi.csv"]:
    if os.path.exists(f):
        df_temp = pd.read_csv(f)
        df_all = pd.concat([df_all, df_temp], ignore_index=True)

if not df_all.empty:
    add_markers_by_type(df_all, groups_dict, search_grp)
    # Зай хэмжигч нэмэх (Зүүн дээд буланд Zoom-ийн доор байрлана)
m.add_child(MeasureControl(
    position='topleft',
    primary_length_unit='kilometers',
    secondary_length_unit='miles',
    primary_area_unit='sqmeters'
))

LocateControl().add_to(m)
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# 1. CSS-ээс бүх Search-тэй холбоотой загварыг устгасан байх ёстой!
# 2. Пайтон хэсэгт зөвхөн ингэж бич:

Search(
    layer=search_grp,
    geom_type='Point',
    placeholder='Хайх...',
    collapsed=True,  # <-- Энэ заавал True
    search_label='search_label'
).add_to(m)
# Google Form-той бүрэн холбогдсон JS код
click_js = """
function onMapClick(e) {
     var lat = e.latlng.lat.toFixed(6);
     var lng = e.latlng.lng.toFixed(6);

     var baseUrl = "https://docs.google.com/forms/d/e/1FAIpQLScNMWMTA4oZpFV2vMeYu8uUJx22Xo8-j_TrjrJY9wppwmn4DQ/viewform?usp=pp_url&entry.711679500=";
     var formUrl = baseUrl + lat + "," + lng;

     // Текстийг зүүн тийш нь шахаж (text-align:left), баруун буланг X товчлуурт суллаж өгөв
     var content = '<div style="text-align: left; font-family: sans-serif; min-width: 220px; padding: 15px 25px 10px 18px; box-sizing: border-box;">' +
                   '<b style="font-size:14px; color:#2c3e50; display:block; margin-bottom:6px; white-space: nowrap;">📍 Шинэ цэг нэмэх үү?</b>' +
                   '<code style="color:#e74c3c; font-size:12px; background:#f8f9fa; padding:2px 6px; border-radius:3px; display:inline-block; margin-bottom:12px; margin-left: 20px;">' + lat + ', ' + lng + '</code><br>' +

                   /* Ногоон товчлуурыг голд нь байрлуулахын тулд тусад нь div-д хийв */
                   '<div style="text-align: center; width: 100%;">' +
                   '<a href="' + formUrl + '" target="_blank" ' +
                   'style="background:#27ae60; color:white; padding:10px 20px; border-radius:25px; text-decoration:none; font-weight:bold; font-size:13px; display:inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">' +
                   'Мэдээлэл илгээх</a>' +
                   '</div>' +
                   '</div>';

     L.popup()
         .setLatLng(e.latlng)
         .setContent(content)
         .openOn(this);
 }

    // Газрын зураг ачаалж дууссаны дараа функцийг холбох
    function initPointPicker() {
        for (var key in window) {
            if (key.startsWith('map_') && window[key] instanceof L.Map) {
                window[key].on('click', onMapClick);
                console.log("Point picker connected to: " + key);
                return;
            }
        }
        setTimeout(initPointPicker, 500);
    }
    initPointPicker();
    """

# Кодоо газрын зурагтаа тарих (Inject)
m.get_root().script.add_child(folium.Element(click_js))
analytics_code = """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-345SKF986B"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-345SKF986B');
    </script>
    """

# Энийг Meta tags нэмдэг хэсэгтээ хамт нэмчихээрэй
m.get_root().header.add_child(folium.Element(analytics_code))

# --- БҮХ УДИРДЛАГА БАРУУН ТАЛД (ХҮЧТЭЙ ХАДАХ ХУВИЛБАР) ---
final_combined_controls = """
<!-- Баруун талын сошиал цонхыг бүх зүйлийн дээр гаргах 🛡️ -->
<div id="right-panel-controls" style="position: fixed; bottom: 20px; right: 20px; z-index: 999999 !important; display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">

    <a href="https://www.facebook.com/sharer/sharer.php?u=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #1877F2; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-facebook-f"></i>
    </a>

    <a href="#" onclick="shareOnMessenger(); return false;"
       style="background: #0084FF; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-facebook-messenger"></i>
    </a>

    <a href="https://t.me/share/url?url=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #0088cc; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-telegram"></i>
    </a>

    <a href="https://twitter.com/intent/tweet?url=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #000000; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-x-twitter"></i>
    </a>

    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #0077b5; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-linkedin-in"></i>
    </a>

    <a href="https://github.com/MongoliaMapGuide/map" target="_blank" 
       style="background: #333; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-github"></i>
    </a>

    <div class="visitor-stats" style="margin-top: 5px; background: white; padding: 2px; border-radius: 4px; box-shadow: 0px 2px 8px rgba(0,0,0,0.2);">
        <img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fbayarchoijil.github.io%2Fmap%2F&labelColor=%2327ae60&countColor=%23555555&style=flat" 
             alt="visitor badge" style="height: 22px; display: block; vertical-align: middle;">
    </div>
</div>

<script>
function shareOnMessenger() {
    var url = "https://mongoliamapguide.github.io/map/";
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (isMobile) {
        window.location.href = "fb-messenger://share/?link=" + encodeURIComponent(url);
    } else {
        window.open("https://www.facebook.com/dialog/send?app_id=1210892749527211&link=" + encodeURIComponent(url) + "&redirect_uri=" + encodeURIComponent(url), "_blank");
    }
}
</script>

<style>
    @media (max-width: 768px) {
        .visitor-stats { display: none !important; }
        .leaflet-popup-content img { max-height: 120px !important; object-fit: cover !important; }
    }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">

<!-- Зүүн талын QR кодыг ч гэсэн хамгийн дээр гаргах 🛡️ -->
<div id="qr-code-container" class="desktop-only" style="
    position: fixed; 
    bottom: 80px; 
    left: 15px; 
    z-index: 999999 !important; 
    background: rgba(255, 255, 255, 0.9); 
    padding: 8px; 
    border-radius: 10px; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    text-align: center;
    border: 1px solid #ddd;
">
    <p style="margin: 0 0 5px 0; font-size: 9px; font-weight: bold; color: #1a73e8; font-family: sans-serif;">SCAN TO MOBILE</p>
    <img src="https://api.qrserver.com/v1/create-qr-code/?size=70x70&data=https://travelmap.mn/?v=76" 
         alt="QR Code" style="width: 70px; height: 70px; display: block;">
</div>
"""
# === БҮХ ДИЗАЙН, УДИРДЛАГЫГ ГАЗРЫН ЗУРАГТ ХОЛБОХ ЖИНХЭНЭ ПАЙТОН КОД ===
m.get_root().html.add_child(folium.Element(final_combined_controls))

# 2. Бүх CSS загваруудыг нэг дор нэгтгэсэн хайрцаг
custom_layout = """
<style>
    /* Гар утас дээр зарим элементүүдийг нуух */
    @media (max-width: 768px) {
        .desktop-only { display: none !important; }
    }

  /* 2. Масштабыг зүүн доод буланд, QR кодтой урагш нь зэрэгцүүлж, доошлуулах */
    .leaflet-control-scale {
        position: fixed !important;
        bottom: 43px !important; /* Доошлуулж, таны нэрний хайрцагтай наалдуулна */
        left: 20px !important;   /* Баруун тийш нь 20px шахаж, QR-ын ирмэгтэй яг таг зэрэгцүүлнэ 🎯 */
        margin: 0 !important;
        z-index: 1000 !important;
    }

    /* Зүүн доод талын таны нэр, зохиогчийн эрхийн хэсгийг ил гаргаж, байрлалыг нь түгжих */
    .leaflet-bottom.leaflet-left {
        position: fixed !important;
        bottom: 10px !important;
        left: 10px !important;
        z-index: 999 !important;
        display: block !important; /* Нуугдсан бол буцааж ил гаргана */
    }

    /* Хэрэв дэлгэц маш жижиг бол цонхыг бага зэрэг шахах */
    @media (max-width: 400px) {
        .leaflet-control-layers-base, 
        .leaflet-control-layers-overlays {
            padding: 8px !important;
        }
        .leaflet-control-layers label {
            font-size: 11px !important;
        }
    }

    /* ПОПАПЫН ЗАСВАР (СААРАЛ ЗАЙГ АРИЛГАХ) */
    .leaflet-popup-content-wrapper { 
        padding: 0 !important; 
        border-radius: 12px !important; 
        overflow: hidden !important; 
        width: auto !important; 
        max-width: 300px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    .leaflet-popup-content { 
        margin: 0 !important; 
        width: auto !important; 
        display: flex !important;
        flex-direction: column !important;
        gap: 0 !important; 
    }

    .leaflet-popup-content img {
        width: 100% !important;
        height: auto !important;
        display: block !important; 
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 12px 12px 0 0 !important;
        object-fit: cover !important;
    }

    .leaflet-popup-close-button { 
        top: 10px !important; 
        right: 10px !important; 
        color: white !important; 
        background: rgba(0,0,0,0.3) !important; 
        border-radius: 50% !important; 
        z-index: 1000 !important; 
    }

    .leaflet-popup-content h3 {
        margin: 0 !important;
        padding: 12px 15px 5px 15px !important;
        font-size: 15px !important;
        font-weight: bold !important;
    }

    .leaflet-popup-content p {
        margin: 0 !important;
        padding: 2px 15px 10px 15px !important;
        font-size: 13px !important;
    }
</style>
<div class="leaflet-bottom leaflet-left" style="pointer-events: auto; margin-bottom: 0px; margin-left: 1px;">
    <div class="leaflet-control-attribution leaflet-control" style="font-size: 11px; padding: 3px 5px; background: rgba(255, 255, 255, 0.8); border-radius: 4px; box-shadow: 0 1px 5px rgba(0,0,0,0.2);">
        &copy; <a href="https://travelmap.mn" target="_blank" style="color: #333; text-decoration: none; font-weight: bold;">2026 TravelMap.mn | BayarChoijil</a>
    </div>
</div>
"""

# 3. Дизайныг газрын зурагтаа холбох
m.get_root().html.add_child(folium.Element(custom_layout))

# 4. Файлаа хадгалах
m.save(os.path.join(current_dir, "index.html"))
print("✨ Төгс хувилбар амжилттай ажиллалаа! Бүх цонх буцаж ирсэн байх ёстой.")

# Зохиогчийн эрхийн фонтыг өөрчилсөн 2026-05-22
import os
import pandas as pd
import folium
from folium.plugins import LocateControl, Search, MarkerCluster, MeasureControl


# 1. МАРКЕР НЭМЭХ ФУНКЦ
def add_markers_by_type(df, groups, search_layer):
    df.columns = df.columns.str.strip()
    df = df.fillna("")
    default_logo = "https://github.com/MongoliaMapGuide/map/blob/main/logo512.png?raw=true"

    for index, row in df.iterrows():
        try:
            # 💡 Баганы нэрсийг таны CSV-тэй яг таг тааруулж авав
            lat = float(row.get('Lat', 0))
            long = float(row.get('Long', 0))
            if lat == 0 or long == 0:
                continue

            p_val = int(float(row.get('Point_type', 1)))

            # Тэмдэгтүүдийг цэвэрлэх
            name_mn = str(row.get('Name_mon', '-')).replace("'", "\\'").strip()
            name_en = str(row.get('Name_eng', '-')).replace("'", "\\'").strip().upper()
            name_kr = str(row.get('Name_kr', '-')).replace("'", "\\'").strip()
            name_jp = str(row.get('Name_jp', '-')).replace("'", "\\'").strip()
            name_cn = str(row.get('Name_cn', '-')).replace("'", "\\'").strip()
            name_ru = str(row.get('Name_ru', '-')).replace("'", "\\'").strip()
            aimag_en = str(row.get('Aimag_name_eng', '-')).strip()
            sum_en = str(row.get('Sum_name_eng', '-')).strip()
            aimag_mn = str(row.get('Aimag_name_mn', aimag_en)).strip()
            photo = str(row.get('Photo_URL', '')).strip()
            phone_val = str(row.get('Phone', '')).strip()
            phone_display = phone_val if phone_val.lower() not in ['nan', 'none', '', '0'] else None

            final_img = photo.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0",
                                                                                              "raw=1") if "http" in photo.lower() else default_logo

            # 🗺️ Икон болон группын мэдээлэл авах
            target_grp, icon_name, icon_color = groups.get(p_val, (None, 'leaf', 'gray'))
            if target_grp is None:
                continue

            # 🌐 Олон хэлний өгөгдөл байхгүй бол англи нэрийг орлуулах хамгаалалт
            kr_title = name_kr if name_kr and name_kr != '-' else name_en
            jp_title = name_jp if name_jp and name_jp != '-' else name_en
            cn_title = name_cn if name_cn and name_cn != '-' else name_en
            ru_title = name_ru if name_ru and name_ru != '-' else name_en

            # 🌐 Олон хэлний өгөгдөл байхгүй бол англи нэрийг орлуулах хамгаалалт
            kr_title = name_kr if name_kr and name_kr != '-' else name_en
            jp_title = name_jp if name_jp and name_jp != '-' else name_en
            cn_title = name_cn if name_cn and name_cn != '-' else name_en
            ru_title = name_ru if name_ru and name_ru != '-' else name_en

            # 📱 Дэд гарчиг - Аль ч хэл дээр ТОГТМОЛ АНГЛИ (Латин) нэрийг жижиг хараар харуулна
            # Класс нэрийг нь "pop-lang-fixed" болгосон тул JavaScript үүнийг оролдож хэл солихгүй, тогтмол үлдэнэ!

            # 📱 Хэл бүрээр харагдах дэд гарчиг, мэдээллийн хэсэг
            lang_section_html = f"""
            <div class="pop-lang-fixed" style="display: block;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇬🇧 {name_en}</div>
            </div>
            """
            lat = row.get('Lat', 0)
            long = row.get('Long', 0)

            # 1. Линк унших ба цэвэрлэх
            fb_raw = str(row.get('Facebook', '')).strip()

            if fb_raw and fb_raw.lower() != 'nan':
                # Урд нь http/https байхгүй бол нэмэх
                if not fb_raw.startswith(('http://', 'https://')):
                    full_url = f"https://{fb_raw}"
                else:
                    full_url = fb_raw

                # Линкийн төрлөөс хамаарч икон, нэр, өнгийг автоматаар тохируулах
                if "facebook.com" in full_url.lower() or "fb.com" in full_url.lower():
                    link_html = f'<div style="margin-bottom: 5px;">🔵 <b>Facebook:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#1877F2; font-weight: 600;">Visit Facebook Page</a></div>'
                elif "instagram.com" in full_url.lower():
                    link_html = f'<div style="margin-bottom: 5px;">📸 <b>Instagram:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#E4405F; font-weight: 600;">Visit Instagram Page</a></div>'
                else:
                    # Хэрэв Фэйсбүүк, Инстаграм биш бол ВЭБСАЙТ гэж үзнэ
                    link_html = f'<div style="margin-bottom: 5px;">🌐 <b>Website:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#008080; font-weight: 600;">Visit Official Website</a></div>'
            else:
                link_html = ""  # Линкгүй бол хоосон байна
            popup_html = f"""
            <div style="width: 280px; min-width: 280px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.15); display: flex; flex-direction: column;">

                <a href="{final_img}" target="_blank" title="Зургийг томсгож үзэх" style="text-decoration: none; display: block; position: relative; cursor: pointer !important;">
                    <div style="width: 100%; max-height: 225px; overflow: hidden; margin: 0; padding: 0; line-height: 0; background: white; display: flex; align-items: center; justify-content: center;">
                        <img src="{final_img}" 
                             style="width: 100%; height: auto; min-height: 225px; object-fit: cover; object-position: center; display: block; margin: 0; border: none; cursor: pointer !important;" 
                             onerror="this.src='https://via.placeholder.com/280x150?text=No+Image'">
                    </div>
                    <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.6); color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-family: sans-serif; pointer-events: none;">🔍 Zoom in</div>
                </a>

                <div style="padding: 10px 15px 15px 15px; margin-top: -1px; background: white; position: relative; z-index: 2;">
                    <div class="pop-lang lang-mn" style="display: block;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{name_mn}</div>
                    </div>
                    <div class="pop-lang lang-en" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{name_en}</div>
                    </div>
                    <div class="pop-lang lang-kr" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{kr_title}</div>
                    </div>
                    <div class="pop-lang lang-jp" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{jp_title}</div>
                    </div>
                    <div class="pop-lang lang-cn" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{cn_title}</div>
                    </div>
                    <div class="pop-lang lang-ru" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 10px 0; line-height: 1.2;">{ru_title}</div>
                    </div>


                    {lang_section_html}

                    <div style="font-size: 11px; color: #444; margin-bottom: 10px; line-height: 1.4; border-top: 1px solid #f5f5f5; padding-top: 10px;">
                        <div style="margin-bottom: 5px;">Location: {sum_en} <b>{aimag_en}</b></div>
                        {f'<div style="margin-bottom: 5px;">Phone: <a href="tel:{phone_display}" style="text-decoration:none; color:#1a73e8; font-weight: 600;">{phone_display}</a></div>' if phone_display else ''}

                        <!-- 🌐 Ухаалаг холбоос (Facebook, Instagram, эсвэл Website болохыг автоматаар ялгаж харуулна) -->
                        {link_html}

                        <div style="margin-top: 8px; color: #555; background: #f8f9fa; padding: 8px; border-radius: 6px; border-left: 3px solid #1a73e8;">
                            <b>GPS:</b>
                            <span style="user-select: all; cursor: pointer; font-family: monospace;">
                            {lat}, {long}
                            </span>
                        </div>
                    </div>

                    <a href="https://www.google.com/maps/search/?api=1&query={lat},{long}" target="_blank"
                       style="display: block; background: #1a73e8; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px; box-shadow: 0 2px 5px rgba(26,115,232,0.3);">
                        🚀 View on Google Maps
                    </a>
                </div>
            </div>
"""

            # Икон тэмдэг үүсгэх HTML
            icon_html = f'<div style="background-color: {icon_color}; border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.4);"><i class="fa-solid fa-{icon_name}" style="font-size: 14px;"></i></div>'

            # 📍 Маркер Кластерт нэмэх хэсэг
            folium.Marker(
                location=[lat, long],
                popup=folium.Popup(popup_html, max_width=280, min_width=280, max_height=425),
                icon=folium.DivIcon(icon_size=(32, 32), icon_anchor=(16, 16), html=icon_html),
                options={
                    'name_mn': name_en,  # <- Монгол хэл дээр доор нь Англи нэр гарна
                    'name_en': name_en,  # <- Англи хэл дээр доор нь Англи нэр гарна
                    'name_kr': name_en,  # <- 🔥 Солонгос хэл дээр ч доор нь Англи нэр гарна!
                    'name_jp': name_en,  # <- 🔥 Япон хэл дээр ч доор нь Англи нэр гарна!
                    'name_cn': name_en,  # <- 🔥 Хятад хэл дээр ч доор нь Англи нэр гарна!
                    'name_ru': name_en  # <- 🔥 Орос хэл дээр ч доор нь Англи нэр гарна!
                }
            ).add_to(target_grp)

            # 🔍 Хайлтад зориулсан далд маркер
            s_marker = folium.CircleMarker(
                location=[lat, long], radius=5, weight=0, fill_color="rgba(0,0,0,0)", color="rgba(0,0,0,0)",
                popup=folium.Popup(popup_html, max_width=280, min_width=280, max_height=425)
            )
            s_marker.options['search_label'] = f"{name_mn} {name_en}".strip()
            s_marker.add_to(search_layer)

        except Exception as e:
            print(f"Мөр {index} дээр алдаа гарлаа: {e}")
            continue


# 2. ҮНДСЭН ХЭСЭГ

# === ГАЗРЫН ЗУРАГ ҮҮСГЭХ ЭХЛЭЛ ХЭСЭГ (ЯГ ИНГЭЖ ЗҮҮН ЗАХАД НААЖ БИЧНЭ 🚀) ===
import os
import folium

# 1. САНГУУДЫН ТОХИРУУЛГА БОЛОН ЗАМЫН ХАВТАС
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. ГАЗРЫН ЗУРАГ ҮҮСГЭХ (Суурийг хоосон үлдээж, масштабыг идэвхжүүлнэ)
m = folium.Map(
    location=[47.0, 103.0],
    zoom_start=6,
    tiles=None,
    max_zoom=17,
    control_scale=True
)

# 3. УЛААВТАР ТЕРРЭЙН ДЭВСПЭРИЙГ БОГИНО НЭРТЭЙГЭЭР НЭМЭХ 🚀
folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr='&copy; OpenTopoMap contributors',
    name="OpenTopoMap",  # Зүүн дээд талын цэвэрхэн нэр ✨
    overlay=False,
    control=True
).add_to(m)
# 2. ДАРАА НЬ БУСАД ЭЛЕМЕНТҮҮД ОРНО ✨
# Одоо 153-р мөрөнд байсан код энд байрлах учраас алдаа заахгүй


# 2. ҮНДСЭН ХЭСЭГ (PWA файлуудыг холбосон хувилбар)
m.get_root().header.add_child(folium.Element("""
<title>TravelMap.mn - Mongolia Travel Guide</title>
<meta name="description" content="Interactive travel guide map of Mongolia.">

<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="shortcut icon" href="/favicon.ico">

<link rel="apple-touch-icon" sizes="180x180" href="/logo180.png">
<link rel="manifest" href="/manifest.json">

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1a73e8">

<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    // Ард нь Date.now() залгаснаар хөтөч үргэлж шинэ хувилбар гэж танина
    navigator.serviceWorker.register('/sw.js?v=' + Date.now()).then(function(registration) {
      console.log('Амжилттай бүртгэгдлээ. Хүрээ: ', registration.scope);
    }).catch(function(err) {
      console.log('Бүртгэл амжилтгүй: ', err);
    });
  });
}
</script>

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1a73e8">


        <meta property="og:title" content="TravelMap.mn - Mongolia Travel Guide">
        <meta property="og:description" content="Interactive travel guide map of Mongolia.">
        <meta property="og:image" content="https://travelmap.mn/logo1200x630.png">
        <meta property="og:url" content="https://travelmap.mn">
        <meta property="og:type" content="website">

        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
        <style>
            .leaflet-popup-content-wrapper { padding: 0 !important; border-radius: 12px !important; overflow: hidden !important; width: 280px !important; }
            .leaflet-popup-content { margin: 0 !important; width: 280px !important; }
            .leaflet-popup-close-button { top: 10px !important; right: 10px !important; color: white !important; background: rgba(0,0,0,0.3) !important; border-radius: 50% !important; z-index: 1000; }
            .leaflet-control-layers { margin-bottom: 20px !important; }
        </style>
  <style>
    /* 1. Хамгийн гадна талын Leaflet контейнерийг цэвэрлэх */
    .leaflet-control-layers,
    .leaflet-control-layers-expanded,
    .leaflet-touch .leaflet-control-layers,
    .leaflet-touch .leaflet-control-layers-expanded {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-top: 15px !important;
        margin-right: 15px !important;
        /* Баруун гар тал руу бүхэлд нь шахах */
        display: flex !important;
        justify-content: flex-end !important;
    }

    /* Хоёр баганыг зэрэгцүүлэх хэсэг */
.leaflet-control-layers-list {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
    background: none !important;
    /* --- ЭНЭ ДООРХ УТГЫГ ӨӨРЧЛӨӨРЭЙ --- */
    gap: 10px !important;  /* 15px-ийг ихэсгэж багасгаж болно */
}

    /* 3. Зүүн талын суурь зураг (Таны хэмжээсүүд) */
    .leaflet-control-layers-base {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 10px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        margin-right: 15px !important; /* Бага зэрэг багасгаж зай хэмнэв */
        flex-shrink: 0 !important;
    }

    /* 4. Баруун талын шүүлтүүр (Таны хэмжээсүүд) */
    .leaflet-control-layers-overlays {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 10px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        flex-shrink: 0 !important;
    }

    /* 5. Бичвэрийн хэмжээ (Таны өгсөн 12px) */
    .leaflet-control-layers label {
        font-size: 12px !important;
        margin-bottom: 5px !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
    }

    .leaflet-control-layers input {
        margin-right: 8px !important;
    }

    /* Хэрэв дэлгэц маш жижиг бол (iPhone SE гэх мэт) цонхыг бага зэрэг шахах */
    @media (max-width: 400px) {
        .leaflet-control-layers-base, 
        .leaflet-control-layers-overlays {
            padding: 8px !important;
        }
        .leaflet-control-layers label {
            font-size: 11px !important;
        }
    }
</style>
    """))

# Tiles (Terrain-ийг буцааж нэмэв)
folium.TileLayer('OpenStreetMap', name='🌐 Street Map').add_to(m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google',
                 name='🛰️ Satellite').add_to(m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google',
                 name='⛰️ Terrain Map').add_to(m)

# Кластер группүүд
nature_grp = MarkerCluster(name='🏞️ Natural Wonders').add_to(m)
hist_grp = MarkerCluster(name='🏛️ Historical Sites').add_to(m)
relig_grp = MarkerCluster(name='🕉️ Religious Sites').add_to(m)
camp_grp = MarkerCluster(name='⛺ Tourist Camps').add_to(m)
resort_grp = MarkerCluster(name='🏢 Resorts').add_to(m)
sanatorium_grp = MarkerCluster(name='🏥 Sanatoriums').add_to(m)
child_grp = MarkerCluster(name='🧒 Children\'s Camps').add_to(m)
service_grp = MarkerCluster(name='🍽️ Roadside Service').add_to(m)
transport_grp = MarkerCluster(name='✈️ Transport').add_to(m)

groups_dict = {
    1: (nature_grp, 'mountain', '#4CAF50'),
    2: (hist_grp, 'landmark', '#2E7D32'),
    3: (relig_grp, 'om', '#FF9800'),
    4: (camp_grp, 'campground', '#673AB7'),
    5: (resort_grp, 'hotel', '#009688'),
    6: (sanatorium_grp, 'briefcase-medical', '#E91E63'),
    7: (child_grp, 'child', '#FF4081'),
    8: (transport_grp, 'plane', '#00838F'),
    9: (transport_grp, 'train', '#0097A7'),
    10: (transport_grp, 'archway', '#00ACC1'),
    11: (service_grp, 'utensils', 'orange'),
    12: (service_grp, 'gas-pump', 'red')
}
search_grp = folium.FeatureGroup(name="Search Layer", control=False).add_to(m)

# Өгөгдөл унших хэсэг (Таны өмнөх кодын дагуу)
df_all = pd.DataFrame()
for f in ["Tourist_camps_multi.csv", "Nature_His_multi.csv"]:
    if os.path.exists(f):
        df_temp = pd.read_csv(f)
        df_all = pd.concat([df_all, df_temp], ignore_index=True)

if not df_all.empty:
    add_markers_by_type(df_all, groups_dict, search_grp)
    # Зай хэмжигч нэмэх (Зүүн дээд буланд Zoom-ийн доор байрлана)
m.add_child(MeasureControl(
    position='topleft',
    primary_length_unit='kilometers',
    secondary_length_unit='miles',
    primary_area_unit='sqmeters'
))

LocateControl().add_to(m)
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# 1. CSS-ээс бүх Search-тэй холбоотой загварыг устгасан байх ёстой!
# 2. Пайтон хэсэгт зөвхөн ингэж бич:

Search(
    layer=search_grp,
    geom_type='Point',
    placeholder='Хайх...',
    collapsed=True,  # <-- Энэ заавал True
    search_label='search_label'
).add_to(m)
# Google Form-той бүрэн холбогдсон JS код
click_js = """
function onMapClick(e) {
     var lat = e.latlng.lat.toFixed(6);
     var lng = e.latlng.lng.toFixed(6);

     var baseUrl = "https://docs.google.com/forms/d/e/1FAIpQLScNMWMTA4oZpFV2vMeYu8uUJx22Xo8-j_TrjrJY9wppwmn4DQ/viewform?usp=pp_url&entry.711679500=";
     var formUrl = baseUrl + lat + "," + lng;

     // Текстийг зүүн тийш нь шахаж (text-align:left), баруун буланг X товчлуурт суллаж өгөв
     var content = '<div style="text-align: left; font-family: sans-serif; min-width: 220px; padding: 15px 25px 10px 18px; box-sizing: border-box;">' +
                   '<b style="font-size:14px; color:#2c3e50; display:block; margin-bottom:6px; white-space: nowrap;">📍 Add a new point?</b>' +
                   '<code style="color:#e74c3c; font-size:12px; background:#f8f9fa; padding:2px 6px; border-radius:3px; display:inline-block; margin-bottom:12px; margin-left: 20px;">' + lat + ', ' + lng + '</code><br>' +

                   /* Ногоон товчлуурыг голд нь байрлуулахын тулд тусад нь div-д хийв */
                   '<div style="text-align: center; width: 100%;">' +
                   '<a href="' + formUrl + '" target="_blank" ' +
                   'style="background:#27ae60; color:white; padding:10px 20px; border-radius:25px; text-decoration:none; font-weight:bold; font-size:13px; display:inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">' +
                   'Send information</a>' +
                   '</div>' +
                   '</div>';

     L.popup()
         .setLatLng(e.latlng)
         .setContent(content)
         .openOn(this);
 }

    // Газрын зураг ачаалж дууссаны дараа функцийг холбох
    function initPointPicker() {
        for (var key in window) {
            if (key.startsWith('map_') && window[key] instanceof L.Map) {
                window[key].on('click', onMapClick);
                console.log("Point picker connected to: " + key);
                return;
            }
        }
        setTimeout(initPointPicker, 500);
    }
    initPointPicker();
    """

# Кодоо газрын зурагтаа тарих (Inject)
m.get_root().script.add_child(folium.Element(click_js))
analytics_code = """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-345SKF986B"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-345SKF986B');
    </script>
    """

# Энийг Meta tags нэмдэг хэсэгтээ хамт нэмчихээрэй
m.get_root().header.add_child(folium.Element(analytics_code))
# --- БҮХ УДИРДЛАГЫГ НЭГТГЭСЭН ЭЦСИЙН ХУВИЛБАР ---
# --- ТОӨЛҮҮР БОЛОН СОШИАЛ УДИРДЛАГА (ЗӨВ ЛИНКТЭЙ ХУВИЛБАР) ---
# --- БҮХ УДИРДЛАГА БАРУУН ТАЛД (СОШИАЛ, ТОӨЛҮҮР, QR КОД) ---
final_combined_controls = """
<div id="right-panel-controls" style="position: fixed; bottom: 20px; right: 20px; z-index: 999999 !important; display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">

    <a href="https://www.facebook.com/sharer/sharer.php?u=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #1877F2; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-facebook-f"></i>
    </a>

    <a href="#" onclick="shareOnMessenger(); return false;"
       style="background: #0084FF; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-facebook-messenger"></i>
    </a>

    <a href="https://t.me/share/url?url=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #0088cc; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-telegram"></i>
    </a>

    <a href="https://twitter.com/intent/tweet?url=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #000000; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-x-twitter"></i>
    </a>

    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://mongoliamapguide.github.io/map/" target="_blank" 
       style="background: #0077b5; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-linkedin-in"></i>
    </a>

    <a href="https://github.com/MongoliaMapGuide/map" target="_blank" 
       style="background: #333; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-github"></i>
    </a>

    <div class="visitor-stats" style="margin-top: 5px; background: white; padding: 2px; border-radius: 4px; box-shadow: 0px 2px 8px rgba(0,0,0,0.2);">
        <img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fbayarchoijil.github.io%2Fmap%2F&labelColor=%2327ae60&countColor=%23555555&style=flat" 
             alt="visitor badge" style="height: 22px; display: block; vertical-align: middle;">
    </div>
</div>

<script>
function shareOnMessenger() {
    var url = "https://mongoliamapguide.github.io/map/";
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (isMobile) {
        window.location.href = "fb-messenger://share/?link=" + encodeURIComponent(url);
    } else {
        window.open("https://www.facebook.com/dialog/send?app_id=1210892749527211&link=" + encodeURIComponent(url) + "&redirect_uri=" + encodeURIComponent(url), "_blank");
    }
}
</script>

<style>
    @media (max-width: 768px) {
        .visitor-stats { display: none !important; }
        .leaflet-popup-content img { max-height: 120px !important; object-fit: cover !important; }
    }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">

<!-- QR кодыг зүүн доод буланд байрлуулах (Зөвхөн Desktop-д) -->
<div id="qr-code-container" class="desktop-only" style="
    position: fixed; 
    bottom: 80px; 
    left: 15px; 
    z-index: 999999 !important; 
    background: rgba(255, 255, 255, 0.9); 
    padding: 8px; 
    border-radius: 10px; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    text-align: center;
    border: 1px solid #ddd;
">
    <p style="margin: 0 0 5px 0; font-size: 9px; font-weight: bold; color: #1a73e8; font-family: sans-serif;">SCAN TO MOBILE</p>
    <img src="https://api.qrserver.com/v1/create-qr-code/?size=70x70&data=https://travelmap.mn/?v=76" 
         alt="QR Code" style="width: 70px; height: 70px; display: block;">
</div>
"""

# --- БҮХ CSS ЗАГВАРУУДЫГ НЭГ ДОР НЭГТГЭСЭН ХАЙРЦАГ ---
custom_layout = """
<style>
    @media (max-width: 768px) {
        .desktop-only { display: none !important; }
    }

    .leaflet-control-scale {
        position: fixed !important;
        bottom: 43px !important; 
        left: 20px !important;   
        margin: 0 !important;
        z-index: 1000 !important;
    }

    .leaflet-bottom.leaflet-left {
        position: fixed !important;
        bottom: 10px !important;
        left: 10px !important;
        z-index: 999 !important;
        display: block !important; 
    }

    @media (max-width: 400px) {
        .leaflet-control-layers-base, 
        .leaflet-control-layers-overlays {
            padding: 8px !important;
        }
        .leaflet-control-layers label {
            font-size: 11px !important;
        }
    }

    .leaflet-popup-content-wrapper { 
        padding: 0 !important; 
        border-radius: 12px !important; 
        overflow: hidden !important; 
        width: auto !important; 
        max-width: 300px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    .leaflet-popup-content { 
        margin: 0 !important; 
        width: auto !important; 
        display: flex !important;
        flex-direction: column !important;
        gap: 0 !important; 
    }

    .leaflet-popup-content img {
        width: 100% !important;
        height: auto !important;
        display: block !important; 
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 12px 12px 0 0 !important;
        object-fit: cover !important;
    }

    .leaflet-popup-close-button { 
        top: 10px !important; 
        right: 10px !important; 
        color: white !important; 
        background: rgba(0,0,0,0.3) !important; 
        border-radius: 50% !important; 
        z-index: 1000 !important; 
    }

    .leaflet-popup-content h3 {
        margin: 0 !important;
        padding: 12px 15px 5px 15px !important;
        font-size: 15px !important;
        font-weight: bold !important;
    }

    .leaflet-popup-content p {
        margin: 0 !important;
        padding: 2px 15px 10px 15px !important;
        font-size: 13px !important;
    }
</style>
<div class="leaflet-bottom leaflet-left" style="pointer-events: auto; margin-bottom: 0px; margin-left: 1px;">
    <div class="leaflet-control-attribution leaflet-control" style="font-size: 11px; padding: 3px 5px; background: rgba(255, 255, 255, 0.8); border-radius: 4px; box-shadow: 0 1px 5px rgba(0,0,0,0.2);">
        &copy; <a href="https://travelmap.mn" target="_blank" style="color: #333; text-decoration: none;">2026 TravelMap.mn | BayarChoijil</a>
    </div>
</div>
"""

# --- ЖИНХЭНЭ АЖИЛЛАХ ПАЙТОН КОДУУД (ХАШИЛТЫН ГАДНА, ДАВХАРДАЛГҮЙ) ---
m.get_root().html.add_child(folium.Element(final_combined_controls))
m.get_root().html.add_child(folium.Element(custom_layout))
# =========================================================================
# 🎯 [ЭЦСИЙН ТӨГС ХУВИЛБАР] ИЛҮҮДЭЛ ХАЙЛТГҮЙ, ПОПАП ЗАССАН ХӨДӨЛГҮҮР 🚀
# =========================================================================

js_libraries = """
<script src="https://unpkg.com/leaflet-search@3.0.9/dist/leaflet-search.src.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet-search@3.0.9/dist/leaflet-search.src.css" />
"""

js_styles = """
<style>
    /* 🌐 ХЭЛНИЙ ЦОНХ ШҮҮЛТҮҮРИЙН ЯГ ДООР БАЙРЛАНА */
    .lang-switcher-panel {
        position: absolute;
        top: 300px;   /* Компьютер дээр баруун талын шүүлтүүрийн доор таарна */
        right: 10px;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.95);
        padding: 4px;
        border-radius: 6px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.35);
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 4px;
        max-width: 130px;
    }
    .lang-btn {
        border: 1px solid #ccc;
        background: #f8f9fa;
        padding: 3px 2px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        font-size: 10px;
        text-align: center;
        transition: all 0.2s;
    }
    .lang-btn.active {
        background: #1a73e8;
        color: white;
        border-color: #1a73e8;
    }
    @media (max-width: 600px) {
        .lang-switcher-panel { top: auto; bottom: 300px; right: 8px; gap: 3px; max-width: 105px; }
        .lang-btn { font-size: 9px; padding: 2px 1px; }
    }

    /* Үндсэн хайлтын загвар (Илүүдэл хайлтыг устгасан тул ганцхан хайлт үлдэнэ) */
    .leaflet-control-search { margin-top: 10px !important; margin-left: 12px !important; }
    .search-target-circle {
        border: 5px solid #ff0000 !important;
        background: rgba(255, 0, 0, 0.15) !important;
        border-radius: 50% !important;
        box-shadow: 0 0 15px #ff0000;
    }
</style>
"""

js_html = """
<div class="lang-switcher-panel" id="langPanel">
    <button class="lang-btn active" data-lang="mn" onclick="switchLanguage('mn')">MN</button>
    <button class="lang-btn" data-lang="en" onclick="switchLanguage('en')">EN</button>
    <button class="lang-btn" data-lang="kr" onclick="switchLanguage('kr')">KR</button>
    <button class="lang-btn" data-lang="jp" onclick="switchLanguage('jp')">JP</button>
    <button class="lang-btn" data-lang="cn" onclick="switchLanguage('cn')">CN</button>
    <button class="lang-btn" data-lang="ru" onclick="switchLanguage('ru')">RU</button>
</div>
"""

js_script = """
<script>
var currentLang = 'mn';
var searchControl = null;
var mapObject = null;
var globalClusterGroups = [];

var dictControlLayers = {
    "Street Map": { "mn": "🌐 Гудамжны зураг", "en": "🌐 Street Map", "kr": "🌐 거리 지도", "jp": "🌐 街路地図", "cn": "🌐 街道地图", "ru": "🌐 Карта улиц" },
    "Satellite": { "mn": "🛰️ Хиймэл дагуул", "en": "🛰️ Satellite", "kr": "🛰️ 위성 지도", "jp": "🛰️ 卫星地图", "cn": "🛰️ 卫星地图", "ru": "🛰️ Спутник" },
    "Terrain Map": { "mn": "⛰️ Гадаргуун зураг", "en": "⛰️ Terrain Map", "kr": "⛰️ 지형 지도", "jp": "⛰️ 地形図", "cn": "⛰️ 地形图", "ru": "⛰️ Карта рельефа" },
    "OpenTopoMap": { "mn": "⛰️ OpenTopoMap", "en": "⛰️ Topo Map", "kr": "⛰️ 등고선 지도", "jp": "⛰️ 地形図", "cn": "⛰️ 地形图", "ru": "⛰️ Топокарта" },

    "Natural Wonders": { "mn": "🏞️ Байгалийн үзэсгэлэн", "en": "Natural Wonders", "kr": "🏞️ 자연 경관", "jp": "🏞️ 自然の景观", "cn": "🏞️ 自然奇观", "ru": "🏞️ Чудеса природы" },
    "Historical Sites": { "mn": "🏛️ Түүхэн дурсгал", "en": "Historical Sites", "kr": "🏛️ 역사 유적지", "jp": "🏛️ 歴史遺跡", "cn": "🏛️ 历史古迹", "ru": "🏛️ Исторические места" },
    "Religious Sites": { "mn": "🕉️ Сүм хийд, шашин", "en": "Religious Sites", "kr": "🕉️ 종교 사원", "jp": "🕉️ 宗教寺院", "cn": "🕉️ 宗教圣地", "ru": "🕉️ Религиозные места" },
    "Tourist Camps": { "mn": "⛺ Жуулчны бааз", "en": "Tourist Camps", "kr": "⛺ 여행자 캠프", "jp": "⛺ ツーリストキャンプ", "cn": "⛺ 旅游营地", "ru": "⛺ Турбазы" },
    "Resorts": { "mn": "🏢 Амралтын газар", "en": "Resorts", "kr": "🏢 리조트", "jp": "🏢 リゾート", "cn": "🏢 度假村", "ru": "🏢 Курорты" },
    "Sanatoriums": { "mn": "🏥 Сувилал", "en": "Sanatoriums", "kr": "🏥 요양원", "jp": "🏥 疗养所", "cn": "🏥 疗养院", "ru": "🏥 Санатории" },
    "Childrens Camps": { "mn": "🧒 Хүүхдийн зуслан", "en": "Children's Camps", "kr": "🧒 어린이 캠프", "jp": "🧒 児童キャンプ", "cn": "🧒 儿童营地", "ru": "🧒 Детские лагеря" },
    "Roadside Service": { "mn": "🍽️ Зам дагуух үйлчилгээ", "en": "Roadside Service", "kr": "🍽️ 길거리 서비스", "jp": "🍽️ ロードサイド", "cn": "🍽️ 路边服务", "ru": "🍽️ Придорожный сервис" },
    "Transport": { "mn": "✈️ Тээвэр, ложистик", "en": "Transport", "kr": "✈️ 교통 / 物流", "jp": "✈️ 交通 / 物流", "cn": "✈️ 交通 / 物流", "ru": "✈️ Транспорт" }
};

document.addEventListener("DOMContentLoaded", function() {
    function initMultilangEngine() {
        for (var key in window) {
            if (key.startsWith('map_') && window[key] instanceof L.Map) { mapObject = window[key]; }
            if (window[key] instanceof L.MarkerClusterGroup) { globalClusterGroups.push(window[key]); }
        }

        if (mapObject) {
            // 💡 Пайтоноос үүссэн илүүдэл, ажилгүй хайлтын цонхыг олж устгах хэсэг
            mapObject.eachLayer(function(layer) {
                if (layer instanceof L.Control.Search && layer !== searchControl) {
                    mapObject.removeControl(layer);
                }
            });

            // Дэлгэц дээрх Folium-ийн хайлтын элементүүдийг устгах
            var badControls = document.querySelectorAll('.leaflet-control-search');
            if (badControls.length > 1) {
                for (var i = 1; i < badControls.length; i++) { badControls[i].remove(); }
            }

            // Попап нээгдэх үеийн хяналт
            mapObject.on('popupopen', function(e) { updatePopupLanguage(); });
            saveOriginalLabels();
        } else {
            setTimeout(initMultilangEngine, 300);
        }
    }
    initMultilangEngine();
});

function saveOriginalLabels() {
    var labels = document.querySelectorAll('.leaflet-control-layers label');
    if (labels.length > 0) {
        labels.forEach(function(label) {
            if (!label.getAttribute('data-raw-text')) {
                var txt = "";
                label.childNodes.forEach(function(node) {
                    if (node.nodeType === 3) txt += node.textContent;
                    else if (node.tagName === 'SPAN' && !node.querySelector('input')) txt += node.textContent;
                });
                if (!txt.trim() || !txt.includes('|')) { txt = label.innerText || ""; }
                txt = txt.trim();
                if (txt) { label.setAttribute('data-raw-text', txt); }
            }
        });
        refreshSearchAndLabels();
    } else {
        setTimeout(saveOriginalLabels, 150);
    }
}

function switchLanguage(lang) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => {
        if(btn.getAttribute('data-lang') === lang) { btn.classList.add('active'); } 
        else { btn.classList.remove('active'); }
    });

    var placeholders = { 'mn':'Газрын нэрээ бичнэ үү...', 'en':'Search location...', 'kr':'위치 검색...', 'jp':'場所を搜索...', 'cn':'搜索地點...', 'ru':'Поиск места...' };
    var inputField = document.querySelector('.search-input');
    if (inputField) { inputField.placeholder = placeholders[lang]; }

    refreshSearchAndLabels();
    updatePopupLanguage();
}

function refreshSearchAndLabels() {
    document.querySelectorAll('.leaflet-control-layers label').forEach(function(label) {
        var rawText = label.getAttribute('data-raw-text');
        if (rawText) {
            var targetText = rawText;
            if (rawText.includes('|')) {
                var parts = rawText.split('|');
                var mnPart = parts[0].trim();
                var enPart = parts[1].trim();
                var cleanEnKey = enPart.replace(/[^a-zA-Z ]/g, "").trim(); 

                if (currentLang === 'mn') {
                    targetText = mnPart;
                } else {
                    var matchedKey = Object.keys(dictControlLayers).find(function(k) {
                        return k.replace(/[^a-zA-Z ]/g, "").toLowerCase() === cleanEnKey.toLowerCase();
                    });
                    targetText = (matchedKey && dictControlLayers[matchedKey][currentLang]) ? dictControlLayers[matchedKey][currentLang] : enPart;
                }
            } else {
                var cleanKey = rawText.replace(/[^a-zA-Z ]/g, "").trim();
                var matchedKey = Object.keys(dictControlLayers).find(function(k) {
                    return k.replace(/[^a-zA-Z ]/g, "").toLowerCase() === cleanKey.toLowerCase();
                });
                if (matchedKey && dictControlLayers[matchedKey][currentLang]) { targetText = dictControlLayers[matchedKey][currentLang]; }
            }

            var textReplaced = false;
            for (var i = 0; i < label.childNodes.length; i++) {
                var node = label.childNodes[i];
                if (node.nodeType === 3 && node.textContent.trim().length > 0) {
                    node.textContent = " " + targetText.trim();
                    textReplaced = true;
                }
            }
            if (!textReplaced) {
                label.querySelectorAll('span').forEach(function(span) {
                    if (!span.querySelector('input')) { span.textContent = targetText.trim(); textReplaced = true; }
                });
            }
        }
    });
}

// 🎯 ПОПАП ОРЧУУЛГЫГ ИДЭВХЖҮҮЛЭХ ЧИГҮҮР
function updatePopupLanguage() {
    document.querySelectorAll('.pop-lang').forEach(function(div) {
        if (div.classList.contains('lang-' + currentLang)) {
            div.style.display = 'block';
        } else {
            div.style.display = 'none';
        }
    });
}
</script>
"""

ultimate_multilang_engine = js_libraries + js_styles + js_html + js_script
m.get_root().html.add_child(folium.Element(ultimate_multilang_engine))
m.save(os.path.join(current_dir, "index.html"))
print("✨ Төгс хувилбар ямар ч алдаагүй, цэвэрхэн ажиллалаа!")
