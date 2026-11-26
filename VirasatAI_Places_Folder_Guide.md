# VirasatAI: Monuments and Nearby Places Folder Guide

Folder preparation completed on 7 October 2026.

The user's selected list contains 20 main monument groups and 200 nearby / less-famous entries. All 220 content entries have folders in Data, Images, Scripts and Audio. This does not mean that all entries are separate physical sites or supported AI classes; site identities and model scope will be checked separately.

Existing Taj Mahal information, scripts, image sources and 40 display images have been preserved.

## Where to find each place

Use the existing numbered project folders. Main monument folders are directly inside each section. Nearby entries are inside their main monument's Nearby_Heritage folder.

Example:

```text
VirasatAI/
  01_Data/
    Taj_Mahal/
      Basic_Info/
      Facts/
      Story_Data/
      Sources/
      Nearby_Heritage/
        Mehtab_Bagh/
          Basic_Info/
          Facts/
          Story_Data/
          Sources/
          README.txt
        nearby_places_index.json
  02_Images/
    Taj_Mahal/
      Nearby_Heritage/
        Mehtab_Bagh/
          Overview/
          Different_Views/
          Details/
          Surroundings/
          Image_Sources/
  03_Scripts/
    Taj_Mahal/
      Nearby_Heritage/
        Mehtab_Bagh/
          English/
          Hindi/
          Voice_Directions/
  04_Audio/
    Taj_Mahal/
      Nearby_Heritage/
        Mehtab_Bagh/
          English/
          Hindi/
```

Each main monument has Basic_Info, Facts, Story_Data and Sources. Each main group also has a nearby index containing the supplied ten entries.

New main-monument image folders start with Front, Back, East, West, North, South, Aerial, Details, Surroundings and Image_Sources. Nearby entries use Overview, Different_Views, Details, Surroundings and Image_Sources. These are organizational categories, not a promise that a photo exists for every view. More site-specific image categories can be added during research. The existing Taj Mahal categories stay unchanged.

English, Hindi and Voice_Directions folders are available for every entry. Audio folders have English and Hindi subfolders.

05_AI_Dataset is separate and was not populated or changed by this content-folder task.

## Selected list

These labels and associations come from the user's table. No places have been substituted or removed.

| # | Main monument group | Main folder | Nearby / less-famous entries |
| --- | --- | --- | --- |
| 1 | Taj Mahal, Agra | Taj_Mahal | Mehtab Bagh; Chini Ka Rauza; The Red Taj (Hessing's Tomb); Taj Nature Walk; Mariam-uz-Zamani Tomb; Ram Bagh; Kanch Mahal; Bateshwar Temples; Jaswant Singh Ki Chhatri; Gurudwara Guru Ka Taal |
| 2 | Qutub Minar, Delhi | Qutub_Minar | Jamali Kamali Mosque; Rajon Ki Baoli; Balban's Tomb; Zafar Mahal; Adham Khan's Tomb; Gandhak Ki Baoli; Hijron Ka Khanqah; Jahaz Mahal; Quli Khan's Tomb; Hauz-i-Shamsi |
| 3 | Amer Fort, Jaipur | Amer_Fort | Panna Meena Ka Kund; Jagat Shiromani Temple; Gaitore Ki Chhatriyan; Anokhi Museum; Galtaji Temple; Garh Ganesh Temple; Vidyadhar Garden; Sagar Lake; Sisodia Rani Ka Bagh; Hathni Kund |
| 4 | Red Fort, Delhi | Red_Fort | Sunehri Masjid; Zeenat-ul-Masajid; Mirza Ghalib Ki Haveli; Chunnamal Haveli; Digambar Jain Bird Hospital; St. James' Church; Khooni Darwaza; Fatehpuri Masjid; Salimgarh Fort; Naughara (Kinari Bazaar) |
| 5 | Gateway of India, Mumbai | Gateway_of_India | Keneseth Eliyahoo Synagogue; Afghan Church; Ballard Bunder Gatehouse; Horniman Circle Gardens; David Sassoon Library; Banganga Tank; Khotachiwadi Village; RBI Monetary Museum; Sewri Fort; Bhau Daji Lad Museum |
| 6 | Charminar, Hyderabad | Charminar | Badshahi Ashurkhana; Purani Haveli; Paigah Tombs; Toli Masjid; Raymond's Tomb; Hayat Bakshi Mosque; Spanish Mosque; Nizam's Museum; Khursheed Jah Devdi; Qutb Shahi Tombs |
| 7 | Victoria Memorial, Kolkata | Victoria_Memorial | South Park Street Cemetery; Lascar War Memorial; Marble Palace; Nipponzan Myohoji Temple; St. John's Church; Mullick Ghat Flower Market; Prinsep Ghat; Jorasanko Thakur Bari; Armenian Church; Magen David Synagogue |
| 8 | Mysore Palace, Mysuru | Mysore_Palace | Jaganmohan Palace; Railway Museum Mysore; Kukkarahalli Lake; Melody World Wax Museum; Kishkindha Moolika Bonsai Garden; St. Philomena's Church Crypt; Gun House; Karanji Lake Aviary; Wellington Lodge; Jayalakshmi Vilas Mansion |
| 9 | Hampi Monuments, Karnataka | Hampi_Monuments | Hemakuta Hill Temples; Matanga Hill; Achyutaraya Temple; Sugriva's Cave; Zenana Enclosure; Badavilinga Temple; Sasivekalu Ganesha; Anegundi Village; Sanapur Lake; Pampa Sarovar |
| 10 | Meenakshi Temple, Madurai | Meenakshi_Temple | Thirumalai Nayakkar Mahal; Gandhi Memorial Museum; Vandiyur Mariamman Teppakulam; Vilachery Pottery Village; Goripalayam Dargah; Koodal Azhagar Temple; Palamuthirsolai Murugan Temple; Kazimar Big Mosque; Yanaimalai; Samanar Hills |
| 11 | Golden Temple, Amritsar | Golden_Temple | Pul Kanjri; Gurdwara Baba Atal Rai; Khalsa College; Ram Bagh Palace; Gobindgarh Fort; Partition Museum; Gurdwara Mata Kaulan; Durgiana Temple; Harike Wetland; Saragarhi Memorial |
| 12 | Khajuraho Monuments, Madhya Pradesh | Khajuraho_Monuments | Raneh Falls; Pandav Falls; Ken Gharial Sanctuary; Matangeshwar Temple; Ajaigarh Fort; Kalinjar Fort; Jain Museum; Duladeo Temple; Chaturbhuj Temple; Beni Sagar Dam |
| 13 | Ajanta & Ellora Caves, Maharashtra | Ajanta_Ellora_Caves | Daulatabad Fort; Bibi Ka Maqbara; Khuldabad; Grishneshwar Jyotirlinga; Siddharth Garden; Salim Ali Lake; Panchakki; Jama Masjid Aurangabad; Soneri Mahal; Bhadra Maruti Temple |
| 14 | Konark Sun Temple, Odisha | Konark_Sun_Temple | Kuruma Buddhist Site; Ramachandi Temple; Chandrabhaga Beach; Astaranga Beach; Barahi Temple (Chaurasi); Pipili Village; Dhauli Shanti Stupa; Chausathi Yogini Temple; Mangalajodi (Chilika); Raghurajpur Artist Village |
| 15 | Sanchi Stupa, Madhya Pradesh | Sanchi_Stupa | Udayagiri Caves; Heliodorus Pillar; Bijamandal; Raisen Fort; Sonari Stupas; Satdhara Stupas; Bhojpur Temple; Andher Stupas; Halali Dam; Neelkantheshwar Temple |
| 16 | City Palace, Udaipur | City_Palace_Udaipur | Ahar Cenotaphs; Sajjangarh (Monsoon Palace); Badi Lake; Saheliyon Ki Bari; Bagore Ki Haveli; Shilpgram; Karni Mata Temple; Ambrai Ghat; Vintage Car Museum; Eklingji Temple |
| 17 | Mahabalipuram, Tamil Nadu | Mahabalipuram | Tiger Cave; Sadras Dutch Fort; Nithyakalyana Perumal Temple; Alamparai Fort; Cholamandal Artists' Village; DakshinaChitra; Muttukadu Backwaters; Vedanthangal Bird Sanctuary; Sri Thiruvidandhai; Poonjeri Village |
| 18 | Jaisalmer Fort, Rajasthan | Jaisalmer_Fort | Kuldhara Village; Bada Bagh; Khaba Fort; Lodhruva Jain Temples; Vyas Chhatri; Desert National Park; Tanot Mata Temple; Akal Wood Fossil Park; Amar Sagar Jain Temple; Nathmal Ji Ki Haveli |
| 19 | Mehrangarh Fort, Jodhpur | Mehrangarh_Fort | Rao Jodha Desert Rock Park; Jaswant Thada; Toorji Ka Jhalra; Mandore Gardens; Balsamand Lake; Mahamandir Temple; Osian Temples; Machia Biological Park; Singhasni Village; Navchowkiya |
| 20 | Badami Cave Temples, Karnataka | Badami_Cave_Temples | Bhutanatha Group of Temples; Agastya Lake; Badami Fort; Mahakuta Group of Temples; Pattadakal Monuments; Aihole (Durga Temple); Banashankari Amma Temple; Ravan Phadi Cave; Lad Khan Temple; Galaganatha Temples |

## Index and progress

- Complete selected-place catalog: 06_Database/JSON/monuments_places_catalog.json
- Folder and existing-file verification: 06_Database/JSON/folder_preparation_report.json
- Per-monument nearby index: 01_Data/<Main_Folder>/Nearby_Heritage/nearby_places_index.json
- Per-place README: 01_Data/<Main_Folder>/README.txt or 01_Data/<Main_Folder>/Nearby_Heritage/<Place_Folder>/README.txt

Current stage: folders prepared. New factual content, English/Hindi master stories, voice directions, audio and Wikimedia images have not yet been added.

## Content preparation rules

1. Verify each site's identity and location before researching facts or selecting images.
2. Prepare Basic_Info, Facts and a source record using government, ASI, UNESCO and official tourism references where available.
3. Select interesting verified facts for Story_Data. Write a connected English/Hindi story and separate voice directions, following the Taj Mahal pattern.
4. Choose clear color photographs from Wikimedia Commons and record the file page, original image URL, photographer, license, attribution, category and local filename.
5. Keep original source references. A gallery image is not automatically an AI training image.
6. Preserve the user's place associations. Do not add unverified distances, travel times, opening hours or ticket prices.

Ajanta & Ellora remain one selected main group. Site-specific material may be stored within the group during content preparation.

The catalog records identity checks for potentially overlapping or ambiguous labels. In particular, Nithyakalyana Perumal Temple and Sri Thiruvidandhai are both retained, as are Purani Haveli and Nizam's Museum. Source verification will decide how to represent their relationship without silently deleting user-selected entries.

