import 'guide_hindi_names.dart';
import 'guide_hindi_locations.dart';

/// Hindi display labels for common heritage terms and locations. Unknown proper
/// names stay in their original spelling until reviewed translations are added.
String guideNameHindi(String name) {
  final exact = guideHindiNames[name];
  if (exact != null) return exact;
  var value = name;
  const words = <String, String>{
    'Taj Mahal': 'ताज महल',
    'Qutub Minar': 'कुतुब मीनार',
    'Red Fort': 'लाल किला',
    'Amer Fort': 'आमेर किला',
    'Gateway of India': 'गेटवे ऑफ इंडिया',
    'Charminar': 'चारमीनार',
    'Victoria Memorial': 'विक्टोरिया मेमोरियल',
    'Mysore Palace': 'मैसूर महल',
    'Hampi Monuments': 'हम्पी स्मारक',
    'Meenakshi Temple': 'मीनाक्षी मंदिर',
    'Golden Temple': 'स्वर्ण मंदिर',
    'Khajuraho Monuments': 'खजुराहो स्मारक',
    'Ajanta & Ellora Caves': 'अजंता और एलोरा गुफाएँ',
    'Konark Sun Temple': 'कोणार्क सूर्य मंदिर',
    'Sanchi Stupa': 'सांची स्तूप',
    'City Palace': 'सिटी पैलेस',
    'Mahabalipuram': 'महाबलीपुरम',
    'Jaisalmer Fort': 'जैसलमेर किला',
    'Mehrangarh Fort': 'मेहरानगढ़ किला',
    'Badami Cave Temples': 'बादामी गुफा मंदिर',
    'Mehtab Bagh': 'मेहताब बाग',
    'Chini Ka Rauza': 'चीनी का रौज़ा',
    'Agra Fort': 'आगरा किला',
    'Itmad-ud-Daulah': 'एतमाद-उद-दौला',
    "The Red Taj (Hessing's Tomb)": 'लाल ताज (हेसिंग का मकबरा)',
    'Taj Nature Walk': 'ताज नेचर वॉक',
    'Mariam-uz-Zamani Tomb': 'मरियम-उज़-ज़मानी का मकबरा',
    'Ram Bagh': 'राम बाग',
    'Kanch Mahal': 'काँच महल',
    'Bateshwar Temples': 'बटेश्वर मंदिर',
    'Jaswant Singh Ki Chhatri': 'जसवंत सिंह की छतरी',
    'Gurudwara Guru Ka Taal': 'गुरुद्वारा गुरु का ताल',
    'Jamali Kamali Mosque': 'जमाली कमाली मस्जिद',
    'Rajon Ki Baoli': 'राजों की बावली',
    "Balban's Tomb": 'बलबन का मकबरा',
    'Zafar Mahal': 'ज़फ़र महल',
    "Adham Khan's Tomb": 'आदम ख़ान का मकबरा',
    'Gandhak Ki Baoli': 'गंधक की बावली',
    'Hijron Ka Khanqah': 'हिजड़ों की ख़ानक़ाह',
    'Jahaz Mahal': 'जहाज़ महल',
    "Quli Khan's Tomb": 'कुली ख़ान का मकबरा',
    'Hauz-i-Shamsi': 'हौज़-ए-शम्सी',
    'Fort': 'किला',
    'Palace': 'महल',
    'Temple': 'मंदिर',
    'Mosque': 'मस्जिद',
    'Tomb': 'मकबरा',
    'Museum': 'संग्रहालय',
    'Gardens': 'बाग',
    'Garden': 'बाग',
    'Gate': 'द्वार',
    'Memorial': 'स्मारक',
    'Caves': 'गुफाएँ',
    'Stupa': 'स्तूप',
  };
  for (final entry in words.entries) {
    value = value.replaceAll(entry.key, entry.value);
  }
  return guideLocationHindi(value);
}

String guideLocationHindi(String location) {
  const reviewed = <String, String>{
    'Across the Yamuna from the Taj Mahal, Agra, Uttar Pradesh':
        'ताज महल के सामने यमुना नदी के पार, आगरा, उत्तर प्रदेश',
    'Yamuna riverbank, Agra, Uttar Pradesh':
        'यमुना नदी का किनारा, आगरा, उत्तर प्रदेश',
    'Roman Catholic Cemetery, Agra, Uttar Pradesh':
        'रोमन कैथोलिक कब्रिस्तान, आगरा, उत्तर प्रदेश',
    'Near the Taj Mahal eastern gate, Agra, Uttar Pradesh':
        'ताज महल के पूर्वी द्वार के पास, आगरा, उत्तर प्रदेश',
    "Southeast of Akbar's Tomb, Sikandra, Agra, Uttar Pradesh":
        'अकबर के मकबरे के दक्षिण-पूर्व में, सिकंदरा, आगरा, उत्तर प्रदेश',
    'Bateshwar, Agra district, Uttar Pradesh':
        'बटेश्वर, आगरा ज़िला, उत्तर प्रदेश',
    'Rajwara area on the Yamuna, Agra, Uttar Pradesh':
        'यमुना किनारे राजवाड़ा क्षेत्र, आगरा, उत्तर प्रदेश',
    'Mehrauli Archaeological Park, Delhi': 'महरौली पुरातत्व उद्यान, दिल्ली',
    'Mehrauli village, Delhi': 'महरौली गाँव, दिल्ली',
    'Mehrauli, Delhi': 'महरौली, दिल्ली',
    'Beside Hauz-i-Shamsi, Mehrauli, Delhi':
        'हौज़-ए-शम्सी के पास, महरौली, दिल्ली',
    'Near Delhi Gate of Red Fort, Delhi':
        'लाल किले के दिल्ली द्वार के पास, दिल्ली',
    'Western end of Chandni Chowk, Delhi': 'चाँदनी चौक का पश्चिमी सिरा, दिल्ली',
    'Sewri, eastern waterfront, Mumbai, Maharashtra':
        'शिवड़ी, पूर्वी तट, मुंबई, महाराष्ट्र',
    'South of Mysore Palace, Mysuru, Karnataka':
        'मैसूर महल के दक्षिण में, मैसूरु, कर्नाटक',
    'East of Madurai, Tamil Nadu': 'मदुरै के पूर्व में, तमिलनाडु',
    'Keelakuyilkudi area, west of Madurai, Tamil Nadu':
        'कीलाकुइलकुडी क्षेत्र, मदुरै के पश्चिम में, तमिलनाडु',
    'Kailashpuri area north of Udaipur, Rajasthan, India':
        'कैलाशपुरी क्षेत्र, उदयपुर के उत्तर में, राजस्थान, भारत',
    'Hill near Gaitore and Nahargarh, Jaipur, Rajasthan':
        'गैटोर और नाहरगढ़ के पास पहाड़ी, जयपुर, राजस्थान',
    'Ken River, Panna and Chhatarpur districts, Madhya Pradesh':
        'केन नदी, पन्ना और छतरपुर ज़िले, मध्य प्रदेश',
    'Halali river, between the Bhopal and Raisen region, Madhya Pradesh, India':
        'हलाली नदी, भोपाल और रायसेन क्षेत्र के बीच, मध्य प्रदेश, भारत',
    'Jaisalmer and Barmer region, Rajasthan':
        'जैसलमेर और बाड़मेर क्षेत्र, राजस्थान',
  };
  if (reviewed.containsKey(location)) return reviewed[location]!;
  var value = location;
  const words = <String, String>{
    'Uttar Pradesh': 'उत्तर प्रदेश',
    'Madhya Pradesh': 'मध्य प्रदेश',
    'Tamil Nadu': 'तमिलनाडु',
    'Rajasthan': 'राजस्थान',
    'Maharashtra': 'महाराष्ट्र',
    'Karnataka': 'कर्नाटक',
    'Odisha': 'ओडिशा',
    'West Bengal': 'पश्चिम बंगाल',
    'Telangana': 'तेलंगाना',
    'Delhi': 'दिल्ली',
    'Agra': 'आगरा',
    'Jaipur': 'जयपुर',
    'Mumbai': 'मुंबई',
    'Hyderabad': 'हैदराबाद',
    'Kolkata': 'कोलकाता',
    'Mysuru': 'मैसूरु',
    'Madurai': 'मदुरै',
    'Amritsar': 'अमृतसर',
    'Udaipur': 'उदयपुर',
    'Jodhpur': 'जोधपुर',
    'Punjab': 'पंजाब',
    'Chennai': 'चेन्नई',
    'Jaisalmer': 'जैसलमेर',
    'Sanchi': 'सांची',
    'Khajuraho': 'खजुराहो',
    'Konark': 'कोणार्क',
    'Hampi': 'हम्पी',
    'Badami': 'बादामी',
    'Mehrauli': 'महरौली',
    'Sikandra': 'सिकंदरा',
    'Bateshwar': 'बटेश्वर',
    'Chhatrapati Sambhajinagar': 'छत्रपति संभाजीनगर',
    'India': 'भारत',
    'Yamuna': 'यमुना',
    'district': 'ज़िला',
    'riverbank': 'नदी का किनारा',
  };
  final replacements = guideHindiLocationTerms.entries.toList()
    ..sort((a, b) => b.key.length.compareTo(a.key.length));
  for (final entry in replacements) {
    value = value.replaceAll(entry.key, entry.value);
  }
  for (final entry in words.entries) {
    value = value.replaceAll(entry.key, entry.value);
  }
  return value;
}
