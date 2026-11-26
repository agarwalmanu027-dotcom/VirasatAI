# VirasatAI Content Library

Updated: 2026-10-08

The selected list contains 20 main monument groups and 200 nearby entries. 218 entries have information and English/Hindi narration scripts. 342 display photographs are saved across 68 entries, including the original 40 Taj Mahal photographs.

## Open and use the files

- Open **VirasatAI_Content_Library.html** to search places, view saved photographs, read the narration and open source links.
- **01_Data** contains Basic_Info, Facts, Story_Data and Sources for each place.
- **02_Images** contains photographs grouped by view. Image_Sources contains each new gallery’s source record and image_manifest.json.
- **03_Scripts** contains English and Hindi master stories. Voice_Directions is guidance for generating audio; it must not be spoken.
- **04_Audio** has prepared folders. Audio files have not been generated or listened to yet.
- **06_Database/JSON/content_library_index.json** connects each place with its files, narration, photographs and status.
- **06_Database/JSON/content_library_audit.json** records checks, sparse galleries and remaining gaps.

## Text-to-speech

For new places, pass only the English or Hindi master-story text to the text-to-speech service. Hindi text uses Devanagari. Sources, filenames and voice directions are separate from the spoken body. Listen to each generated recording and check place-name pronunciation before using it in the app.

For Taj Mahal, use taj_mahal_tts_body_english.txt and taj_mahal_tts_body_hindi.txt. These copies remove only the original heading. The original master stories are unchanged. The pilot story is longer than most new stories; the duration in the index is an estimate.

## Image quality and source credits

New photographs were screened for resolution and colour, then visually reviewed for the correct place, clarity and composition. Wrong-city photographs, low-resolution images, visible watermarks, black-and-white photographs and poor images were rejected. There is no fixed photo quota: a sparse gallery is safer than adding unsuitable photographs.

Wikimedia restricted original-file downloads during collection. Existing saved originals remain unchanged. New downloads use Wikimedia’s supported high-resolution sizes, commonly 1920 or 3840 pixels wide. No photograph was enlarged. The manifest records both original dimensions and actual saved dimensions.

Use the photographer name, license and source-page link in the image manifest when showing a photograph in the application. Some preserved Taj Mahal source-record fields still say VERIFY; check these legacy fields before publication. Photo licenses are separate from factual source references.

## Entries that need identity clarification

- **Hathni Kund**: Exact Jaipur site identity needs further reliable-source verification.
- **Galaganatha Temples**: Identity pending by user instruction: Aihole group or Pattadakal temple.

Sri Thiruvidandhai and Nithyakalyana Perumal Temple refer to the same temple/locality. Both user-selected labels are retained. Nearby associations follow the supplied list and do not prove distance or travel time.

## Coverage by group

| Group | Content ready / 11 | Saved photographs | Places with photographs / 11 |
| --- | ---: | ---: | ---: |
| Taj Mahal, Agra | 11 | 70 | 10 |
| Qutub Minar, Delhi | 11 | 55 | 11 |
| Amer Fort, Jaipur | 10 | 36 | 8 |
| Red Fort, Delhi | 11 | 27 | 8 |
| Gateway of India, Mumbai | 11 | 50 | 11 |
| Charminar, Hyderabad | 11 | 48 | 10 |
| Victoria Memorial, Kolkata | 11 | 47 | 9 |
| Mysore Palace, Mysuru | 11 | 9 | 1 |
| Hampi Monuments, Karnataka | 11 | 0 | 0 |
| Meenakshi Temple, Madurai | 11 | 0 | 0 |
| Golden Temple, Amritsar | 11 | 0 | 0 |
| Khajuraho Monuments, Madhya Pradesh | 11 | 0 | 0 |
| Ajanta & Ellora Caves, Maharashtra | 11 | 0 | 0 |
| Konark Sun Temple, Odisha | 11 | 0 | 0 |
| Sanchi Stupa, Madhya Pradesh | 11 | 0 | 0 |
| City Palace, Udaipur | 11 | 0 | 0 |
| Mahabalipuram, Tamil Nadu | 11 | 0 | 0 |
| Jaisalmer Fort, Rajasthan | 11 | 0 | 0 |
| Mehrangarh Fort, Jodhpur | 11 | 0 | 0 |
| Badami Cave Temples, Karnataka | 10 | 0 | 0 |

## Places without suitable saved photographs

These entries remain visible as pending in the library. They are not filled with photographs of other places.

- **Bateshwar Temples** (Taj Mahal, Agra): Correct Agra/UP identity checked. Morena images rejected; two Agra interior candidates rejected for noise and soft detail. High-quality exterior gallery pending.
- **Vidyadhar Garden** (Amer Fort, Jaipur): Generic Jaipur street photograph rejected. Qualifying correctly identified garden photographs pending.
- **Sagar Lake** (Amer Fort, Jaipur): Man Sagar/Jal Mahal photographs rejected. Correct identity is the reservoir behind Amer Fort; qualifying images pending.
- **Hathni Kund** (Amer Fort, Jaipur): Exact Jaipur site identity needs further reliable-source verification.
- **Chunnamal Haveli** (Red Fort, Delhi): No reviewed high-quality, correct-site image saved yet.
- **St. James' Church** (Red Fort, Delhi): No reviewed high-quality, correct-site image saved yet.
- **Naughara (Kinari Bazaar)** (Red Fort, Delhi): No reviewed high-quality, correct-site image saved yet.
- **Hayat Bakshi Mosque** (Charminar, Hyderabad): All ten candidates depict the Hayat Bakshi funerary mosque inside the Qutb Shahi Tombs complex. The intended entry is the mosque/sarai at Hayathnagar; no candidate selected until a correctly identified Hayathnagar photo is available.
- **Marble Palace** (Victoria Memorial, Kolkata): No reviewed high-quality, correct-site image saved yet.
- **Nipponzan Myohoji Temple** (Victoria Memorial, Kolkata): No reviewed high-quality, correct-site image saved yet.
- **Jaganmohan Palace** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Railway Museum Mysore** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Kukkarahalli Lake** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Melody World Wax Museum** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Kishkindha Moolika Bonsai Garden** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **St. Philomena's Church Crypt** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Gun House** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Karanji Lake Aviary** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Wellington Lodge** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Jayalakshmi Vilas Mansion** (Mysore Palace, Mysuru): No reviewed high-quality, correct-site image saved yet.
- **Hampi Monuments, Karnataka** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Hemakuta Hill Temples** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Matanga Hill** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Achyutaraya Temple** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Sugriva's Cave** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Zenana Enclosure** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Badavilinga Temple** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Sasivekalu Ganesha** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Anegundi Village** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Sanapur Lake** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Pampa Sarovar** (Hampi Monuments, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Meenakshi Temple, Madurai** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Thirumalai Nayakkar Mahal** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Gandhi Memorial Museum** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Vandiyur Mariamman Teppakulam** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Vilachery Pottery Village** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Goripalayam Dargah** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Koodal Azhagar Temple** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Palamuthirsolai Murugan Temple** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Kazimar Big Mosque** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Yanaimalai** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Samanar Hills** (Meenakshi Temple, Madurai): No reviewed high-quality, correct-site image saved yet.
- **Golden Temple, Amritsar** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Pul Kanjri** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Gurdwara Baba Atal Rai** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Khalsa College** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Ram Bagh Palace** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Gobindgarh Fort** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Partition Museum** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Gurdwara Mata Kaulan** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Durgiana Temple** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Harike Wetland** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Saragarhi Memorial** (Golden Temple, Amritsar): No reviewed high-quality, correct-site image saved yet.
- **Khajuraho Monuments, Madhya Pradesh** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Raneh Falls** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Pandav Falls** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Ken Gharial Sanctuary** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Matangeshwar Temple** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Ajaigarh Fort** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Kalinjar Fort** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Jain Museum** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Duladeo Temple** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Chaturbhuj Temple** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Beni Sagar Dam** (Khajuraho Monuments, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Ajanta & Ellora Caves, Maharashtra** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Daulatabad Fort** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Bibi Ka Maqbara** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Khuldabad** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Grishneshwar Jyotirlinga** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Siddharth Garden** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Salim Ali Lake** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Panchakki** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Jama Masjid Aurangabad** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Soneri Mahal** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Bhadra Maruti Temple** (Ajanta & Ellora Caves, Maharashtra): No reviewed high-quality, correct-site image saved yet.
- **Konark Sun Temple, Odisha** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Kuruma Buddhist Site** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Ramachandi Temple** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Chandrabhaga Beach** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Astaranga Beach** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Barahi Temple (Chaurasi)** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Pipili Village** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Dhauli Shanti Stupa** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Chausathi Yogini Temple** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Mangalajodi (Chilika)** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Raghurajpur Artist Village** (Konark Sun Temple, Odisha): No reviewed high-quality, correct-site image saved yet.
- **Sanchi Stupa, Madhya Pradesh** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Udayagiri Caves** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Heliodorus Pillar** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Bijamandal** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Raisen Fort** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Sonari Stupas** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Satdhara Stupas** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Bhojpur Temple** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Andher Stupas** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Halali Dam** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **Neelkantheshwar Temple** (Sanchi Stupa, Madhya Pradesh): No reviewed high-quality, correct-site image saved yet.
- **City Palace, Udaipur** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Ahar Cenotaphs** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Sajjangarh (Monsoon Palace)** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Badi Lake** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Saheliyon Ki Bari** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Bagore Ki Haveli** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Shilpgram** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Karni Mata Temple** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Ambrai Ghat** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Vintage Car Museum** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Eklingji Temple** (City Palace, Udaipur): No reviewed high-quality, correct-site image saved yet.
- **Mahabalipuram, Tamil Nadu** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Tiger Cave** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Sadras Dutch Fort** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Nithyakalyana Perumal Temple** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Alamparai Fort** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Cholamandal Artists' Village** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **DakshinaChitra** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Muttukadu Backwaters** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Vedanthangal Bird Sanctuary** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Sri Thiruvidandhai** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Poonjeri Village** (Mahabalipuram, Tamil Nadu): No reviewed high-quality, correct-site image saved yet.
- **Jaisalmer Fort, Rajasthan** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Kuldhara Village** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Bada Bagh** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Khaba Fort** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Lodhruva Jain Temples** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Vyas Chhatri** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Desert National Park** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Tanot Mata Temple** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Akal Wood Fossil Park** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Amar Sagar Jain Temple** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Nathmal Ji Ki Haveli** (Jaisalmer Fort, Rajasthan): No reviewed high-quality, correct-site image saved yet.
- **Mehrangarh Fort, Jodhpur** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Rao Jodha Desert Rock Park** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Jaswant Thada** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Toorji Ka Jhalra** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Mandore Gardens** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Balsamand Lake** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Mahamandir Temple** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Osian Temples** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Machia Biological Park** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Singhasni Village** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Navchowkiya** (Mehrangarh Fort, Jodhpur): No reviewed high-quality, correct-site image saved yet.
- **Badami Cave Temples, Karnataka** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Bhutanatha Group of Temples** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Agastya Lake** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Badami Fort** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Mahakuta Group of Temples** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Pattadakal Monuments** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Aihole (Durga Temple)** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Banashankari Amma Temple** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Ravan Phadi Cave** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Lad Khan Temple** (Badami Cave Temples, Karnataka): No reviewed high-quality, correct-site image saved yet.
- **Galaganatha Temples** (Badami Cave Temples, Karnataka): Identity pending by user instruction: Aihole group or Pattadakal temple.

## Project boundary

This is the display-content library. It does not mean that the AI model recognises all listed places. The training dataset was not changed. App features, model training, authority integration and report submission still need their own implementation and testing.

All 49 protected original pilot files passed the saved SHA-256 comparison.
