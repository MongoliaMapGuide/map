import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, Search, LocateControl


def add_markers_by_type(df, nature_grp, camp_grp, service_grp, transport_grp, search_grp):
    df.columns = df.columns.str.strip()
    df = df.fillna("")

    for index, row in df.iterrows():
        try:
            lat = pd.to_numeric(row.get('Lat'), errors='coerce')
            lon = pd.to_numeric(row.get('Long'), errors='coerce')
            if pd.isna(lat) or pd.isna(lon): continue

            # Мэдээллүүд
            name_en = str(row.get('Name_eng', '')).strip().upper()
            name_mn = str(row.get('Name_mon', '')).strip()
            name_kr = str(row.get('Name_kr', '')).strip()
            name_jp = str(row.get('Name_jp', '')).strip()
            name_cn = str(row.get('Name_cn', '')).strip()
            name_ru = str(row.get('Name_ru', '')).strip()

            aimag_mn = str(row.get('Aimag_name_mon', '')).strip()
            sum_mn = str(row.get('Sum_name_mon', '')).strip()
            aimag_en = str(row.get('Aimag_name_eng', '')).strip()
            sum_en = str(row.get('Sum_name_eng', '')).strip()

            phone = str(row.get('Phone', '')).strip()
            photo = str(row.get('Photo_URL', '')).strip()
            point_type = int(row.get('Point_type', 0)) if str(row.get('Point_type')).isdigit() else 0

            # 🎨 Икон ба Давхарга сонгох (Ангиллыг зөв хуваарилах)
            if 1 <= point_type <= 5:  # Жуулчны бааз
                target_grp, icon_name, icon_color = camp_grp, 'landmark', 'purple'
            elif point_type == 6:  # Замын гуанз
                target_grp, icon_name, icon_color = service_grp, 'cutlery', 'orange'
            elif point_type == 10:  # ШТС
                target_grp, icon_name, icon_color = service_grp, 'gas-pump', 'red'

            # --- TRANSPORT ХЭСЭГ (Энийг салгах хэрэгтэй) ---
            elif point_type == 7:  # Нисэх буудал
                target_grp, icon_name, icon_color = transport_grp, 'plane', 'cadetblue'
            elif point_type == 8:  # Боомт
                target_grp, icon_name, icon_color = transport_grp, 'truck', 'blue'
            elif point_type == 9:  # Өртөө
                target_grp, icon_name, icon_color = transport_grp, 'train', 'darkblue'

            else:  # Байгаль, түүхэн газар (Point_type == 0 эсвэл бусад)
                target_grp, icon_name, icon_color = nature_grp, 'leaf', 'green'

            # 🖼️ Зураг засагч
            img_html = ""
            if photo.startswith("http"):
                fixed_photo = photo.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "raw=1")
                img_html = f'<img src="{fixed_photo}" style="width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">'
            google_maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

            # 📝 Поп-ап (Бүх 6 хэлтэй)
            popup_html = f"""
            <div style="font-family: Arial; min-width: 240px; color: #333;">
                {img_html}
                <div style="text-align: center; margin-bottom: 8px;">
                    <b style="font-size: 15px; color: #1a73e8; display: block;">{name_en}</b>
                    <b style="font-size: 13px; color: #555; display: block;">{name_mn}</b>
                </div>
                <div style="font-size: 11px; color: #666; background: #f9f9f9; padding: 6px; border-radius: 5px; margin-bottom: 8px; border-left: 3px solid #1a73e8;">
                    🇰🇷 {name_kr}<br>🇯🇵 {name_jp}<br>🇨🇳 {name_cn}<br>🇷🇺 {name_ru}
                </div>
                <div style="font-size: 12px; line-height: 1.4;">
                    <b>📍 MN:</b> {aimag_mn}, {sum_mn}<br>
                    <b>📍 EN:</b> {aimag_en}, {sum_en}<br>
                    {f'<b>📞 Phone:</b> {phone}<br>' if phone else ''}
                    <b>🌍 GPS:</b> {lat}, {lon}
                </div>
                <div style="margin-top: 10px; text-align: center;">
                    <a href="{google_maps_link}" target="_blank" style="background: #4285F4; color: white; padding: 8px 15px; text-decoration: none; border-radius: 20px; font-size: 11px; font-weight: bold; display: inline-block;">📍 View on Google Maps</a>
                </div>
            </div>
            """

            # 1. Үндсэн маркер (Кластер давхаргад)
            marker = folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
            ).add_to(target_grp)

            # 2. ХАЙЛТЫН ТӨЛӨӨЛӨГЧ (Мөсөн уул шиг, харагдахгүй ч хайлтанд ашиглагдана)
            # 2. ХАЙЛТЫН ТӨЛӨӨЛӨГЧ (Үл үзэгдэгч болгож засав)
            folium.GeoJson(
                data={
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {"name": f"{name_en} {name_mn}"}
                },
                # style_function ашиглан цэгийг үл үзэгдэгч болгож байна
                style_function=lambda x: {
                    'fillColor': '#ffffff00',  # 00 гэдэг нь тунгалаг гэсэн үг
                    'color': '#ffffff00',
                    'radius': 0
                },
                # Маркерын оронд жижиг тойрог ашиглах (ингэснээр хөх тэмдэг гарахгүй)
                marker=folium.CircleMarker(radius=0, fill_color='#ffffff00', color='#ffffff00'),
                tooltip=name_en,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(search_grp)

        except:
            continue


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    m = folium.Map(location=[47.0, 103.0], zoom_start=6, tiles=None)

    # 🗺️ СУУРЬ ЗУРГУУД (Terrain нэмэгдсэн)
    folium.TileLayer('OpenStreetMap', name='🌐 Street Map').add_to(m)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google',
                     name='🛰️ Satellite').add_to(m)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google',
                     name='⛰️ Terrain Map').add_to(m)

    nature_grp = MarkerCluster(name="🌳 Nature & History").add_to(m)
    camp_grp = MarkerCluster(name="⛺ Tourist Camps").add_to(m)
    service_grp = MarkerCluster(name="⛽ Roadside Service").add_to(m)
    transport_grp = MarkerCluster(name="✈️ Transport").add_to(m)
    search_grp = folium.FeatureGroup(name="Search Layer", control=False).add_to(m)

    try:
        df = pd.read_csv(os.path.join(current_dir, "Tourist_camps_multi.csv"))
        nature_path = os.path.join(current_dir, "Nature_HIs_multi.csv")
        if os.path.exists(nature_path):
            df_nature = pd.read_csv(nature_path)
            df_nature['Point_type'] = 0
            df = pd.concat([df, df_nature], ignore_index=True)

        add_markers_by_type(df, nature_grp, camp_grp, service_grp, transport_grp, search_grp)
    except Exception as e:
        print(f"Error: {e}")
        # 🛠️ ХЭРЭГСЛҮҮД
        # search_label='name' гэдэг нь дээрх CircleMarker-ийн name утгатай таарах ёстой
    Search(
        layer=search_grp,
        geom_type='Point',
        placeholder='Search (Name / Нэр)...',
        collapsed=False,
        search_label='name'  # <--- Энэ маш чухал!
    ).add_to(m)

    LocateControl().add_to(m)
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    # --- VISITORS: ӨНӨӨДӨР / НИЙТ (Visitorbadge API) ---
# Энэ хэсгийг бүхлээр нь хуулж өмнөх counter_html-ээ сольно
counter_html = """
<div style="position: fixed; 
            bottom: 20px; left: 20px; 
            z-index:9999; 
            display: flex;
            flex-direction: column;
            gap: 10px;">

   <div style="display: flex; gap: 8px;">
        <a href="https://www.facebook.com/sharer/sharer.php?u=https://mongoliamapguide.github.io/map/" 
           target="_blank" 
           style="background-color: #1877F2; color: white; padding: 8px 15px; border-radius: 50px; 
                  text-decoration: none; font-family: Arial, sans-serif; font-size: 12px; font-weight: bold;
                  display: flex; align-items: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
           <i class="fa-brands fa-facebook" style="margin-right: 5px;"></i> Share
        </a>

       <a href="#" 
           onclick="shareOnMessenger(); return false;"
           style="background-color: #0084FF; color: white; padding: 8px 15px; border-radius: 50px; 
                  text-decoration: none; font-family: Arial, sans-serif; font-size: 12px; font-weight: bold;
                  display: flex; align-items: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
           <i class="fa-brands fa-facebook-messenger" style="margin-right: 5px;"></i> Send
        </a>

        <script>
        function shareOnMessenger() {
            var url = "https://mongoliamapguide.github.io/map/";
            // Гар утас мөн эсэхийг шалгах
            var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

            if (isMobile) {
                // Гар утас бол шууд Апп-ыг нь дуудна
                window.location.href = "fb-messenger://share/?link=" + encodeURIComponent(url);
            } else {
                // PC бол Вэб диалогийг нээнэ
                window.open("https://www.facebook.com/dialog/send?app_id=1210892749527211&link=" + encodeURIComponent(url) + "&redirect_uri=" + encodeURIComponent(url), "_blank");
            }
        }
        </script>
    </div>

    <div style="display: flex; align-items: center; background-color: white; padding: 5px 15px;
                border-radius: 50px; border: 2px solid #27ae60; box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
                font-family: Arial, sans-serif; width: fit-content;">
        <span style="font-weight: bold; color: #333; margin-right: 10px; font-size: 13px;">ЗОЧИД:</span>
        <img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fbayarchoijil.github.io%2Fmap%2F&labelColor=%2327ae60&countColor=%23555555&style=flat" 
             alt="visitor badge" style="border-radius: 4px; vertical-align: middle;">
    </div>
</div>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
"""

# Таны 191-р мөрөнд байгаа код одоо алдаагүй ажиллана
m.get_root().html.add_child(folium.Element(counter_html))

# --- Meta Tag-уудыг бэлдэх хэсэг ---
meta_tags = """
    <meta charset="UTF-8">
    <link rel="manifest" href="manifest.json">
    <title>Mongolia Map Guide - Interactive Travel Platform</title>
    <meta name="description" content="Discover 1,651+ destinations across Mongolia. Interactive map for resorts, historical sites, and nature.">

    <meta property="og:type" content="website">
    <meta property="og:url" content="https://mongoliamapguide.github.io/map/">
    <meta property="og:title" content="🇲🇳 Mongolia Map Guide: Explore the Land of Eternal Blue Sky">
    <meta property="og:description" content="1,651+ points of interest. Seamless navigation in 6 languages.">

    <meta property="og:image" content="https://github.com/user-attachments/assets/3df95d79-b3b2-469b-a58e-5f83a6d25168">

    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="Mongolia Map Guide">
    <meta property="twitter:image" content="https://github.com/user-attachments/assets/3df95d79-b3b2-469b-a58e-5f83a6d25168">
    """

# Folium-ийн header-т meta tag-уудыг нэмэх
m.get_root().header.add_child(folium.Element(meta_tags))

# 1. Файл хадгалах замыг нэг хувьсагчид авъя
output_path = os.path.join(current_dir, "index.html")

# 🎬 ЭНД ВИДЕО ЗААВАР НЭМЭХ ХЭСЭГ (m.save-ийн яг өмнө)
tutorial_html = """
    <style>
        #video-chat-box { position: fixed; top: 260px; left: 10px; z-index: 10000; font-family: 'Segoe UI', Arial, sans-serif; }
        .video-btn { background-color: #ff5722; color: white; padding: 8px 14px; border-radius: 6px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-weight: bold; font-size: 12px; display: flex; align-items: center; gap: 6px; border: 1px solid white; }
        #tutorial-window { display: none; background: white; padding: 8px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); width: 320px; margin-top: 10px; border: 1px solid #ddd; overflow: hidden; }
        .close-btn { float: right; cursor: pointer; font-size: 20px; font-weight: bold; color: #666; padding-right: 5px; }
    </style>

    <div id="video-chat-box">
        <div class="video-btn" onclick="document.getElementById('tutorial-window').style.display='block'">
            🎬 ▶ Ашиглах заавар
        </div>
        <div id="tutorial-window">
            <span class="close-btn" onclick="document.getElementById('tutorial-window').style.display='none'">&times;</span>
            <div style="padding: 10px; font-weight: bold; background: #f8f9fa; border-bottom: 1px solid #eee;">📖 Видео заавар</div>
            <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                <iframe src="https://www.youtube.com/embed/1ju-nFngcvI" 
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                        frameborder="0" allowfullscreen>
                </iframe>
            </div>
        </div>
    </div>
    """

# 🔗 HTML-ийг газрын зураг руу "наах"
m.get_root().html.add_child(folium.Element(tutorial_html))

# 💾 ФАЙЛАА ХАДГАЛАХ
m.save(os.path.join(current_dir, "index.html"))
# 1. Файлаа унших
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 2. Нэмэх кодууд (Manifest болон Service Worker)
pwa_tags = """
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#1a73e8">
    <link rel="apple-touch-icon" href="logo512.png">
"""

pwa_script = """
    <script>
      if ('service-worker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('./service-worker.js')
            .then(reg => console.log('Апп амжилттай бүртгэгдлээ!'))
            .catch(err => console.log('Алдаа:', err));
        });
      }
    </script>
"""

# 3. HTML-ийн толгой болон хөл хэсэгт кодыг "тарьж" өгөх
html_content = html_content.replace('</head>', f'{pwa_tags}</head>')
html_content = html_content.replace('</body>', f'{pwa_script}</body>')

# 4. Буцааж хадгалах
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("PWA код 'index.html'-д амжилттай нэмэгдлээ!")
print("✅ Meta tags болон Манифест амжилттай нэмэгдлээ!")
print("✨ Хайлт болон Terrain зураг бэлэн боллоо!")

