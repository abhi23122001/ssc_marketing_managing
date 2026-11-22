# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Autonomous Daily AI Marketing Intelligence & Strategy Engine.

Provides:
  1. Rich library of 14 specialized engineering pillars for SSC and 10 for INFRA.
  2. Non-repeating strategy generator: records prior recommendations, avoids duplication.
  3. Actionable daily practical instructions: target audience, video format, duration,
     opening hook, full video script (spoken Hindi + English), shot-by-shot visual instructions,
     required field footage, voiceover, on-screen text, CTA, and thumbnail concept.
  4. Platform-specific campaign optimizations for Instagram, Facebook, and YouTube Shorts:
     distinct captions, hashtags, keywords, titles, CTAs, thumbnail guidance, posting times,
     compliance notes, and tracking plans.
  5. Content workflow bridge: Save strategy directly to Content Calendar (`social_content_items`).
  6. Verified industry research database and tender opportunity synthesizer.
"""
from __future__ import annotations

import json
import os
import sqlite3
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..store import Store

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))


def now_kolkata() -> datetime:
    return datetime.now(KOLKATA_TZ)


def now_kolkata_iso() -> str:
    return now_kolkata().strftime("%Y-%m-%dT%H:%M:%S%z")


def now_kolkata_date() -> str:
    return now_kolkata().strftime("%Y-%m-%d")


# =============================================================================
# 1. SSC Specialized Engineering Strategy Pillars (14 Non-Repeating Pillars)
# =============================================================================
SSC_PILLARS = [
    {
        "id": "DGPS_RTK_ACCURACY",
        "service": "Dual-Frequency DGPS RTK Land Surveying",
        "title": "Why 2cm Accuracy Matters: DGPS RTK vs Handheld GPS in Land Boundaries",
        "relevance": "Land demarcation disputes along state highways & private acquisitions in Central India",
        "target_audience": "Land Developers, PWD Highway Contractors, Industrial Plant Heads, Legal Property Owners",
        "video_format": "9:16 Vertical Video / Instagram Reel & YouTube Short",
        "duration": "38 - 45 seconds",
        "hook": "क्या आपकी 5 एकड़ जमीन की बाउंड्री वाकई सही है? एक मामूली 2 मीटर की गलती से लाखों का नुकसान कैसे होता है?",
        "script_parts": {
            "hook": "क्या आपको पता है कि नॉर्मल मोबाइल या हैंडहेल्ड जीपीएस में 3 से 5 मीटर तक का एरर होता है? और जब जमीन की कीमत करोड़ों में हो, तो 2 मीटर की गलती का मतलब है लाखों का नुकसान!",
            "problem": "कई बार बिना प्रॉपर बेंचमार्क के की गई बाउंड्री आगे चलकर पड़ोसी से विवाद या सरकारी डिमार्केशन में रिजेक्ट हो जाती है।",
            "solution": "शाह सर्वेयर्स का डुअल-फ्रीक्वेंसी DGPS RTK सिस्टम सर्वे ऑफ इंडिया के GTS पिलर से कनेक्ट होकर मिलीमीटर लेवल (±10mm) एक्यूरेसी लॉक करता है। 18+ सैटेलाइट्स और रियल-टाइम बेस-रोवर करेक्शन के साथ!",
            "cta": "अपनी साइट पर 100% सर्टिफाइड और डिस्प्यूट-फ्री लैंड सर्वे के लिए आज ही शाह सर्वेयर्स से संपर्क करें। 24 घंटे में साइट इंस्पेक्शन और कोटेशन उपलब्ध!"
        },
        "shot_by_shot": [
            {"shot": 1, "visual": "Close-up of surveyor leveling the circular bubble vial on DGPS rover pole", "audio": "Punchy warning chime + Spoken Hook", "text": "2 Meter Error = ₹10 Lakh Loss!"},
            {"shot": 2, "visual": "Rover data collector screen displaying 'RTK FIXED', 18 Satellites, Horizontal Accuracy: 0.008m", "audio": "Fast-paced tech explanation", "text": "±8mm High Precision RTK Fix"},
            {"shot": 3, "visual": "Surveyor marking permanent RCC benchmark pillar on site with red paint", "audio": "Explanation of Survey of India GTS datum", "text": "Survey of India GTS Linked"},
            {"shot": 4, "visual": "AutoCAD screen with coordinate grid and company contact card overlay", "audio": "Clear CTA voiceover", "text": "Call: +91 98222 00000 | Shah Surveyors"}
        ],
        "required_footage": "Leica/Trimble DGPS rover setup, handheld controller screen showing RTK Fixed, permanent concrete pillar, AutoCAD CAD drawing export.",
        "voiceover": "क्या आपको पता है नॉर्मल जीपीएस में 3 से 5 मीटर का एरर होता है? शाह सर्वेयर्स का डुअल-फ्रीक्वेंसी RTK सिस्टम देता है ±10mm की एक्यूरेसी। डिस्प्यूट-फ्री लैंड सर्वे के लिए कॉल करें +91 98222 00000।",
        "on_screen_text": ["Handheld GPS = 5m Error", "Shah RTK DGPS = ±10mm Fix", "Certified by MoRTH/SoI Norms", "Book Survey Today"],
        "cta": "Contact Shah Surveyors at +91 98222 00000 or click link in bio for instant certified DGPS survey quote.",
        "thumbnail_concept": "High contrast split screen: Red cross over inaccurate tape measure vs Bright Green checkmark on Leica DGPS rover with bold text: '2cm vs 5m Error!'",
        "platforms": {
            "instagram": {
                "format": "9:16 Vertical Reel (38s)",
                "caption": "⚠️ क्या आपकी जमीन की बाउंड्री वाकई सेफ है?\n\nकई प्रोजेक्ट्स सिर्फ इसलिए अटक जाते हैं क्योंकि शुरुआती सर्वे में 2 मीटर का फर्क रह गया था।\n\nशाह सर्वेयर्स का RTK DGPS सिस्टम:\n✅ ±10mm पिनपॉइंट एक्यूरेसी\n✅ सर्वे ऑफ इंडिया GTS पिलर से लिंक्ड\n✅ KML, DWG और सर्टिफाइड रिपोर्ट 24 घंटे में\n\n📌 सेंट्रल इंडिया और नागपुर रीजन में फास्ट डिप्लॉयमेंट।\n\n📲 DM करें या बायो में लिंक पर क्लिक करके फ्री कंसल्टेशन बुक करें!\n\n#DGPS #LandSurvey #SurveyingIndia #CivilEngineering #NagpurRealEstate #PropertySurvey #RTK #ShahGroup #SurveyOfIndia #LandMeasurement",
                "hashtags": ["#DGPS", "#LandSurvey", "#SurveyingIndia", "#CivilEngineering", "#PropertySurvey", "#RTK", "#ShahGroup", "#SurveyOfIndia", "#Topography", "#CAD"],
                "keywords": ["dgps survey nagpur", "rtk land measurement", "boundary demarcation india", "survey of india benchmark"],
                "timing": "17:45 - 19:15 IST (Prime evening window for contractors and landowners)",
                "cta": "DM for instant project quote"
            },
            "facebook": {
                "format": "Video Case Study / Page Update",
                "title": "Eliminating Boundary Disputes: Why High-Precision RTK DGPS is Critical for Highway & Industrial Land",
                "caption": "Project delays due to ambiguous site boundaries cost Indian infrastructure developers millions annually. Handheld GPS devices carry up to 5-meter positional errors—completely unacceptable for highway ROW (Right of Way) or industrial zoning.\n\nShah Surveyors & Consultancy deploys dual-frequency multi-constellation RTK GNSS receivers tied to Survey of India GTS benchmarks, delivering certified sub-centimeter (±10mm) coordinates.\n\nOur Field Deliverables:\n• Geo-referenced Boundary KML & DWG CAD files\n• Permanent RCC benchmark pillar establishment\n• Legal compliance documentation for registry & PWD approvals\n\n📍 Serving Maharashtra, MP & Central India.\n📞 Contact our engineering desk at +91 98222 00000 for site inspection bookings.",
                "hashtags": ["#InfrastructureEngineering", "#LandSurveying", "#DGPS", "#MoRTH", "#HighwayEngineering", "#ShahSurveyors"],
                "keywords": ["DGPS survey contractor", "highway ROW demarcation", "industrial land survey", "survey of india benchmark"],
                "timing": "11:30 AM - 01:30 PM IST (Commercial desk hours for EPC procurement heads)",
                "cta": "WhatsApp / Call Engineering Desk"
            },
            "youtube_shorts": {
                "format": "9:16 Vertical Short (45s)",
                "title": "DGPS Survey vs Normal GPS: 2cm vs 5m Accuracy Explained! #Shorts",
                "description": "Watch how dual-frequency RTK DGPS survey eliminates land boundary disputes with ±10mm accuracy connected to Survey of India GTS datum. Shah Surveyors & Consultancy provides high-precision surveying across Central India.\n\nEquipment Used: Leica RTK GNSS Receiver\nAccuracy: Horizontal 8mm, Vertical 15mm\n\n📞 Inquiries: +91 98222 00000\n🌐 Website: https://shahgroup.co.in",
                "hashtags": ["#Shorts", "#DGPS", "#CivilEngineering", "#LandSurvey", "#SurveyOfIndia"],
                "keywords": ["how dgps works", "dgps survey in hindi", "land boundary survey accuracy", "rtk vs gps"],
                "timing": "18:30 - 20:30 IST",
                "cta": "Subscribe for civil engineering insights & comment your project location!"
            }
        }
    },
    {
        "id": "DRONE_LIDAR_CANOPY",
        "service": "Drone LiDAR & High-Density Topographical Mapping",
        "title": "Drone LiDAR Penetration: Measuring Bare Ground Under Dense Tree Cover",
        "relevance": "Forest road alignments, hilly terrain DPRs, and irrigation reservoir surveys",
        "target_audience": "NHAI DPR Consultants, Forest Department Contractors, Irrigation Engineers, Mining Surveyors",
        "video_format": "9:16 Vertical Video / Reel",
        "duration": "40 - 48 seconds",
        "hook": "जब घने पेड़ों और झाड़ियों के नीचे जमीन मापनी हो, तो नॉर्मल कैमरा ड्रोन फेल क्यों हो जाता है?",
        "script_parts": {
            "hook": "क्या आपको पता है कि नॉर्मल फोटोग्रामेट्री ड्रोन सिर्फ पेड़ों की पत्तियों की फोटो लेता है, नीचे की असली जमीन नहीं देख पाता?",
            "problem": "घने जंगलों या झाड़ीदार पहाड़ी जमीन पर अगर नॉर्मल ड्रोन चलाएं, तो कंटूर में 1 से 2 मीटर तक का गलत एलिवेशन आ जाता है।",
            "solution": "लेकिन शाह सर्वेयर्स का 'Drone LiDAR' सिस्टम हर सेकंड लाखों लेजर पल्स भेजता है जो पत्तियों के बीच से निकलकर असली जमीन को छूते हैं। नतीजा? 100% एक्यूरेट डिजिटल टेरेन मॉडल (DTM)!",
            "cta": "घने जंगलों, घाट सेक्शन और पहाड़ी प्रोजेक्ट्स के लिए शाह सर्वेयर्स की LiDAR टीम से संपर्क करें।"
        },
        "shot_by_shot": [
            {"shot": 1, "visual": "Drone hovering over dense green tree canopy, then graphic lasers beam through foliage to the ground", "audio": "Whoosh sound + Spoken Hook", "text": "Can Normal Drones See Through Trees?"},
            {"shot": 2, "visual": "Side-by-side 3D point cloud: Left raw canopy points; Right ground classified DTM points", "audio": "Technical explanation of multi-return LiDAR", "text": "Bare Earth DTM Extracted"},
            {"shot": 3, "visual": "Contour lines overlaid with 0.5m interval over elevation gradient map", "audio": "Accuracy proof", "text": "0.5m Contour Accuracy in Forest"},
            {"shot": 4, "visual": "Drone pilot landing hexacopter safely with DGCA logo and contact details", "audio": "CTA voiceover", "text": "Certified LiDAR Mapping | Shah Group"}
        ],
        "required_footage": "Hexacopter drone takeoff, 3D LiDAR point cloud colorized by elevation, screen capture of ground classification in TerraSolid/GlobalMapper.",
        "voiceover": "नॉर्मल ड्रोन सिर्फ पेड़ों की पत्तियां देखता है, लेकिन शाह सर्वेयर्स का LiDAR सिस्टम पत्तों के आर-पार जाकर जमीन का सही DTM निकालता है। सर्टिफाइड LiDAR सर्वे के लिए कॉल करें +91 98222 00000।",
        "on_screen_text": ["Camera Drone = Canopy Only", "LiDAR = True Bare Earth DTM", "±5cm Vertical Accuracy", "Book Drone LiDAR"],
        "cta": "Call +91 98222 00000 to deploy DGCA-certified Drone LiDAR teams.",
        "thumbnail_concept": "Graphic cross-section showing laser rays piercing through dark green trees to brown ground with neon text: 'LiDAR Sees Through Trees!'",
        "platforms": {
            "instagram": {
                "format": "9:16 Vertical Reel (42s)",
                "caption": "🌲 जब घने जंगल में जमीन का सर्वे करना हो, तो साधारण कैमरा ड्रोन फेल हो जाता है!\n\nक्यों? क्योंकि फोटोग्रामेट्री सिर्फ पत्तियों की फोटो खींचती है, असली जमीन नहीं।\n\nशाह सर्वेयर्स का Drone LiDAR:\n📡 Multi-return laser pulses\n🌿 पत्तों को भेदकर असली ज़मीन (Bare Earth DTM) कैप्चर करता है\n⛰️ घाट सेक्शन, हाईवे अलाइनमेंट और माइनिंग के लिए बेस्ट\n\nDGCA सर्टिफाइड पायलट और एडवांस्ड सेंसर्स के साथ सेंट्रल इंडिया में उपलब्ध।\n\n📩 कोटेशन के लिए DM करें!\n\n#DroneLiDAR #LiDARIndia #TopographicalSurvey #ForestSurvey #CivilEngineering #ShahGroup #DroneMapping",
                "hashtags": ["#DroneLiDAR", "#LiDARIndia", "#TopographicalSurvey", "#ForestSurvey", "#CivilEngineering", "#ShahGroup"],
                "keywords": ["drone lidar survey india", "bare earth dtm forest", "lidar contour mapping"],
                "timing": "18:00 - 19:30 IST",
                "cta": "DM for LiDAR quote"
            },
            "facebook": {
                "format": "Technical Video Showcase",
                "title": "Ground Penetrating Aerial LiDAR: Delivering True DTM Under Heavy Forest Canopy",
                "caption": "Conducting Detailed Project Reports (DPR) in forested corridors or hilly alignments has historically meant slow, hazardous physical total station traverses. Optical photogrammetry fails because passive cameras cannot see through dense vegetative cover.\n\nShah Surveyors & Consultancy solves this with high-repetition multi-return Aerial LiDAR. By capturing multiple pulse returns, our processing pipeline strips vegetative clutter to extract true bare-earth elevations with 0.5m contour fidelity.\n\nApplications:\n• Highway Ghat Alignments & Railway DPRs\n• Irrigation Reservoir Submergence Studies\n• Mining Overburden & Stockpile Volumetrics\n\nContact our technical team at +91 98222 00000 for technical proposals.",
                "hashtags": ["#DroneLiDAR", "#Geospatial", "#CivilInfra", "#NHAI", "#SurveyConsultants"],
                "keywords": ["aerial lidar contractor india", "forest survey dtm", "contour survey lidar"],
                "timing": "12:00 - 02:00 PM IST",
                "cta": "Request Engineering Proposal"
            },
            "youtube_shorts": {
                "format": "9:16 Vertical Short (48s)",
                "title": "How Drone LiDAR Sees Through Dense Forests! #Shorts",
                "description": "Optical drones only capture tree tops, but Drone LiDAR fires 200,000 laser pulses per second to penetrate vegetation and map bare ground elevations. Watch how Shah Surveyors extracts DTM point clouds for highway DPRs.\n\n📞 Contact: +91 98222 00000 | Shah Surveyors & Consultancy",
                "hashtags": ["#Shorts", "#DroneLiDAR", "#Engineering", "#LiDAR"],
                "keywords": ["drone lidar in forest", "point cloud classification", "surveying technology"],
                "timing": "19:00 - 21:00 IST",
                "cta": "Subscribe for high-tech survey demonstrations!"
            }
        }
    },
    {
        "id": "HIGHWAY_FLS_ALIGNMENT",
        "service": "Highway FLS (Final Location Survey) & Alignment Pegging",
        "title": "MoRTH Highway FLS: Fast-Track Centerline Pegging with RCC Boundary Pillars",
        "relevance": "NHAI & State PWD 4-lane expressway and bypass expansion tenders",
        "target_audience": "Highway Concessionaires, EPC Project Directors, PWD Executive Engineers",
        "video_format": "9:16 Vertical Video / Reel",
        "duration": "35 - 42 seconds",
        "hook": "हाईवे प्रोजेक्ट्स में टेंडर मिलने के बाद सबसे पहला क्रिटिकल माइलस्टोन क्या होता है?",
        "script_parts": {
            "hook": "हाईवे टेंडर अवॉर्ड होते ही सबसे पहला क्रिटिकल काम होता है: FLS यानी Final Location Survey और सेंटरलाइन पेगिंग!",
            "problem": "अगर सेंटरलाइन पेगिंग में जरा भी डेवििएशन आया, तो अर्थवर्क कटिंग-फिलिंग का बजट करोड़ों में मिसमैच हो जाता है।",
            "solution": "शाह सर्वेयर्स की टीम MoRTH और IRC-SP-19 नॉर्म्स के मुताबिक 20-20 मीटर पर सेंटरलाइन पेगिंग और हर 200 मीटर पर परमानेंट RCC पिलर्स एस्टैब्लिश करती है।",
            "cta": "अपने हाईवे और एक्सप्रेसवे प्रोजेक्ट्स के लिए सर्टिफाइड FLS टीम डिप्लॉय कराएं। संपर्क करें शाह सर्वेयर्स।"
        },
        "shot_by_shot": [
            {"shot": 1, "visual": "Highway corridor with surveyor looking through optical sight of Total Station", "audio": "Upbeat site music + Spoken Hook", "text": "Highway FLS Milestone"},
            {"shot": 2, "visual": "Survey assistant driving wooden peg at 20m chainage mark with yellow spray paint", "audio": "Explanation of 20m chainage pegging", "text": "20m Chainage Centerline Pegging"},
            {"shot": 3, "visual": "Pre-cast RCC boundary pillar marked 'NHAI ROW' planted firmly in ground", "audio": "MoRTH Section & IRC compliance", "text": "MoRTH & IRC-SP-19 Compliant"},
            {"shot": 4, "visual": "Complete L-Section and Cross-Section CAD sheet rolling out on site table", "audio": "Call to action", "text": "Certified FLS | Shah Surveyors"}
        ],
        "required_footage": "Total station sighting on highway corridor, chainage pegging with hammer, RCC pillar installation, L-section drawing.",
        "voiceover": "हाईवे प्रोजेक्ट्स में सेंटरलाइन और FLS में गलती मतलब करोड़ों का अर्थवर्क नुकसान। शाह सर्वेयर्स देता है MoRTH कंप्लायंट FLS और 20m पेगिंग। कॉल करें +91 98222 00000।",
        "on_screen_text": ["Highway FLS Survey", "20m Interval Pegging", "MoRTH Standard Pillars", "Contact Shah Group"],
        "cta": "Call +91 98222 00000 for certified Highway FLS survey deployment.",
        "thumbnail_concept": "Surveyor with Total Station on open highway corridor with bold yellow text: 'Highway FLS in 7 Days!'",
        "platforms": {
            "instagram": {
                "format": "9:16 Vertical Reel (38s)",
                "caption": "🛣️ हाईवे कांट्रैक्ट मिलते ही सबसे पहला काम: FLS यानी Final Location Survey!\n\nसेंटरलाइन पेगिंग में 10cm का भी फर्क अर्थवर्क के पूरे बजट को बिगाड़ सकता है।\n\nशाह सर्वेयर्स:\n📍 MoRTH & IRC-SP-19 नॉर्म्स के तहत 20m इंटरवल पेगिंग\n📍 परमानेंट RCC बाउंड्री पिलर्स फिक्सेशन\n📍 L-Section & Cross-Section CAD शीट्स\n\nहाईवे और एक्सप्रेसवे प्रोजेक्ट्स के लिए अनुभवी टीम।\n\n📞 कॉल: +91 98222 00000\n\n#HighwayEngineering #FLS #LandSurvey #MoRTH #CivilEngineersIndia #ShahGroup",
                "hashtags": ["#HighwayEngineering", "#FLS", "#LandSurvey", "#MoRTH", "#CivilEngineersIndia"],
                "keywords": ["highway final location survey", "centerline pegging morth", "fls survey contractor"],
                "timing": "17:30 - 19:00 IST",
                "cta": "Call now for site schedule"
            },
            "facebook": {
                "format": "Project Execution Post",
                "title": "MoRTH Compliant Highway Final Location Survey (FLS) & Centerline Pegging",
                "caption": "Fast-tracking highway construction begins with meticulous Final Location Surveys (FLS). Shah Surveyors & Consultancy provides turnkey alignment establishment adhering to IRC-SP-19 guidelines.\n\nScope of Work Delivered:\n1. Centerline coordinate transfer from DGPS GTS datum at 20-meter intervals.\n2. Permanent Pre-cast RCC ROW boundary pillar planting.\n3. Detailed L-section and cross-sections at 20m and at all culvert/structure locations.\n\nProven track record with NHAI, PWD, and major EPC concessionaires across Central India.\n\nContact us for project mobilization: +91 98222 00000",
                "hashtags": ["#HighwayConstruction", "#FLS", "#CivilEngineering", "#NHAI", "#EPCContractor"],
                "keywords": ["highway fls survey", "irc sp 19 alignment", "road centerline pegging"],
                "timing": "11:45 AM - 01:15 PM IST",
                "cta": "Contact Project Lead"
            },
            "youtube_shorts": {
                "format": "9:16 Vertical Short (42s)",
                "title": "What is Highway FLS & Centerline Pegging? #Shorts",
                "description": "Learn how highway engineers establish 20m centerline chainage and RCC boundary pillars as per MoRTH specifications. Shah Surveyors & Consultancy delivers fast, accurate FLS surveys across India.\n\nInquiries: +91 98222 00000",
                "hashtags": ["#Shorts", "#HighwayEngineering", "#FLS", "#CivilEngineering"],
                "keywords": ["fls survey in road construction", "highway pegging", "civil engineering shorts"],
                "timing": "18:00 - 20:00 IST",
                "cta": "Subscribe for daily civil engineering shorts!"
            }
        }
    },
    {
        "id": "MINING_IBM_RULE34A",
        "service": "Mining Lease Volumetric Surveys & IBM Rule 34A Compliance",
        "title": "Mining Lease Volume Compliance: Drone Photogrammetry Under IBM Rule 34A",
        "relevance": "Mandatory annual IBM compliance for coal, limestone, iron ore, and bauxite mines",
        "target_audience": "Mine Owners, Mining Agents, Geologists, Quarry Operators",
        "video_format": "9:16 Vertical Video / Reel",
        "duration": "38 - 45 seconds",
        "hook": "माइंस ओनर्स ध्यान दें: क्या आपकी एनुअल IBM Rule 34A ड्रोन सर्वे रिपोर्ट तैयार है?",
        "script_parts": {
            "hook": "माइंस ओनर्स ध्यान दें! इंडियन ब्यूरो ऑफ माइन्स (IBM) Rule 34A के तहत हर साल 1 जुलाई से पहले लीज एरिया का डिजिटल 3D ड्रोन सर्वे जमा करना अनिवार्य है।",
            "problem": "अगर सर्वे में डिमार्केशन एरर या अनऑथराइज्ड माइनिंग डिटेक्ट हुई, तो पेनल्टी और लीज सस्पेंशन का रिस्क हो सकता है।",
            "solution": "शाह सर्वेयर्स की टीम DGCA-सर्टिफाइड ड्रोन्स से पिट वॉल्यूम, ओवरबर्डन डंप्स और लीज बाउंड्री का 3D पॉइंट क्लाउड बनाती है—पूरी तरह IBM स्पेसिफिकेशन कंप्लायंट!",
            "cta": "अंतिम तारीख से पहले अपनी खदान का 3D ड्रोन सर्वे शेड्यूल कराने के लिए तुरंत कॉल करें।"
        },
        "shot_by_shot": [
            {"shot": 1, "visual": "Aerial drone shot descending into deep open-cast mining pit with heavy dumpers", "audio": "Heavy industrial hum + Spoken Hook", "text": "IBM Rule 34A Compliance"},
            {"shot": 2, "visual": "3D wireframe mesh calculating exact cubic meters of overburden dump", "audio": "Explanation of volume cut/fill accuracy", "text": "Pit & Dump Volumetric Cut/Fill"},
            {"shot": 3, "visual": "Mining boundary overlay in red with zero encroachment certificate stamp", "audio": "IBM certified reporting", "text": "100% Boundary Encroachment Audit"},
            {"shot": 4, "visual": "Mining surveyor handing certified report folder to site manager", "audio": "CTA voiceover", "text": "Book Mining Survey | Shah Group"}
        ],
        "required_footage": "Open cast mine aerial drone view, 3D mesh volume cut/fill calculation in software, mine boundary KML, certified IBM report binder.",
        "voiceover": "IBM Rule 34A के तहत अपनी माइन का एनुअल 3D ड्रोन सर्वे समय पर कराएं। पिट वॉल्यूम, ओवरबर्डन डंप और बाउंड्री का सटीक डेटा। कॉल करें शाह सर्वेयर्स +91 98222 00000।",
        "on_screen_text": ["IBM Rule 34A Mandatory", "3D Volumetric Audit", "Pit & Overburden Calculations", "Call Shah Surveyors"],
        "cta": "Call +91 98222 00000 to schedule your IBM Rule 34A mine drone survey.",
        "thumbnail_concept": "Massive open cast mine pit with yellow 3D grid lines and bold text: 'IBM Mining Drone Survey'",
        "platforms": {
            "instagram": {
                "format": "9:16 Vertical Reel (40s)",
                "caption": "⛏️ माइंस ओनर्स और लीज होल्डर्स के लिए जरूरी सूचना!\n\nIBM Rule 34A के तहत खदान का डिजिटल 3D ड्रोन सर्वे कराना अनिवार्य है।\n\nशाह सर्वेयर्स की माइनिंग सर्वे सर्विस:\n✅ ओवरबर्डन (OB) डंप वॉल्यूम कैलकुलेशन\n✅ पिट एक्सकैवेशन वॉल्यूम सर्टिफिकेशन\n✅ लीज बाउंड्री पिलर वेरिफिकेशन\n✅ IBM कंप्लायंट 3D पॉइंट क्लाउड और KML\n\nसेंट्रल इंडिया की प्रमुख माइंस के साथ काम करने का अनुभव।\n\n📲 तुरंत संपर्क करें: +91 98222 00000\n\n#MiningIndia #IBMRule34A #DroneSurvey #OpenCastMining #CoalMining #ShahGroup",
                "hashtags": ["#MiningIndia", "#IBMRule34A", "#DroneSurvey", "#OpenCastMining", "#CoalMining"],
                "keywords": ["ibm rule 34a drone survey", "mining lease volume measurement", "mine volumetric survey india"],
                "timing": "17:45 - 19:15 IST",
                "cta": "Book Mine Survey Today"
            },
            "facebook": {
                "format": "Industry Technical Compliance Post",
                "title": "Indian Bureau of Mines (IBM) Rule 34A Compliance: Turnkey Drone Volumetric Surveys",
                "caption": "Under Rule 34A of Mineral Conservation and Development Rules (MCDR), mining leaseholders must submit high-resolution ortho-rectified imagery and digital elevation models (DEM) annually to the Indian Bureau of Mines.\n\nShah Surveyors & Consultancy delivers complete compliance:\n• Sub-centimeter RTK ground control network (DGPS)\n• Volumetric calculation of active pits and overburden dumps (m³)\n• Boundary buffer analysis ensuring zero off-lease encroachment\n• Signed engineering reports formatted to IBM portal upload standards.\n\nProtect your mining concession from statutory notices. Schedule your annual survey: +91 98222 00000",
                "hashtags": ["#MiningIndustry", "#MCDR", "#DroneVolumetrics", "#MiningIndia", "#ShahSurveyors"],
                "keywords": ["ibm rule 34a compliance", "mining drone survey central india", "mine volume audit"],
                "timing": "11:30 AM - 01:30 PM IST",
                "cta": "Contact Mining Survey Lead"
            },
            "youtube_shorts": {
                "format": "9:16 Vertical Short (44s)",
                "title": "How Drones Calculate Mine Pit Volume in 3D! #Shorts",
                "description": "See how DGCA-certified drones and photogrammetry software calculate millions of cubic meters of mining excavation for IBM Rule 34A compliance. Shah Surveyors provides certified mining surveys across India.\n\nCall: +91 98222 00000",
                "hashtags": ["#Shorts", "#Mining", "#DroneSurvey", "#CivilEngineering"],
                "keywords": ["mine pit volume drone", "ibm rule 34a", "mining engineering"],
                "timing": "18:30 - 20:30 IST",
                "cta": "Subscribe for more surveying tech videos!"
            }
        }
    },
    {
        "id": "GPR_UTILITY_SCAN",
        "service": "Subsurface Utility Engineering (GPR Scanning)",
        "title": "Zero Pipe Damages: Underground Utility Detection with Dual-Frequency GPR",
        "relevance": "Smart city projects, gas pipelines, trenchless drilling (HDD), and fiber optic cable corridors",
        "target_audience": "Gas Distribution Companies, Smart City Contractors, Telecom EPCs, Municipal Engineers",
        "video_format": "9:16 Vertical Video / Reel",
        "duration": "35 - 42 seconds",
        "hook": "सड़क की खुदाई शुरू करने से पहले कैसे पता करें कि 3 मीटर नीचे कौन सी पाइप या बिजली की केबल दबी है?",
        "script_parts": {
            "hook": "सड़क पर बिना जांचे जेसीबी से खुदाई शुरू करना सबसे बड़ा रिस्क है! एक पाइप या फाइबर केबल कटी, तो लाखों का जुर्माना और काम हफ्तों के लिए बंद!",
            "problem": "पुराने नगर निगम नक्शों में अंडरग्राउंड पाइपलाइन की लोकेशन 80% मामलों में गलत दर्ज होती है।",
            "solution": "शाह सर्वेयर्स का डुअल-फ्रीक्वेंसी Ground Penetrating Radar (GPR) बिना एक फावड़ा चलाए 5 मीटर गहराई तक पानी, गैस, सीवर और इलेक्ट्रिक केबल्स का 3D मैप बना देता है।",
            "cta": "खुदाई से पहले अपनी साइट का GPR यूटिलिटी स्कैन कराएं और पेनल्टी से बचें। कॉल करें शाह सर्वेयर्स।"
        },
        "shot_by_shot": [
            {"shot": 1, "visual": "JCB bucket stopped just inches above a yellow gas pipeline with warning siren effect", "audio": "Siren alert + Spoken Hook", "text": "Avoid Underground Cable Damage!"},
            {"shot": 2, "visual": "Surveyor pushing dual-frequency GPR cart across asphalt road", "audio": "Explanation of radar waves penetrating ground", "text": "Dual-Frequency GPR Scanning"},
            {"shot": 3, "visual": "Radargram screen showing distinct hyperbola curves marking 3 buried pipelines", "audio": "Accuracy & depth detection", "text": "Exact Depth & Position Mapped"},
            {"shot": 4, "visual": "Finished 3D utility layout map overlaid on Google Earth street view", "audio": "CTA voiceover", "text": "Safe Digging | Shah Surveyors"}
        ],
        "required_footage": "GPR cart pushed along urban road, screen showing radar hyperbolas, CAD utility color-coded lines, warning tape on excavation site.",
        "voiceover": "बिना जांचे खुदाई से गैस पाइप या फाइबर केबल कटने पर लाखों का जुर्माना हो सकता है। शाह सर्वेयर्स का GPR स्कैन बिना गड्ढा खोदे 5 मीटर नीचे तक सब दिखा देता है। कॉल करें +91 98222 00000।",
        "on_screen_text": ["Avoid Utility Cuts", "GPR Penetrates 5m Deep", "Gas, Power, Water Mapped", "Call Shah Surveyors"],
        "cta": "Call +91 98222 00000 for non-destructive GPR underground utility scanning.",
        "thumbnail_concept": "Cross section of asphalt road showing radar waves revealing buried pipes with bold text: 'See Underground Before Digging!'",
        "platforms": {
            "instagram": {
                "format": "9:16 Vertical Reel (36s)",
                "caption": "⚠️ जेसीबी चलाने से पहले सावधान!\n\nसड़क के नीचे क्या दबा है—गैस पाइपलाइन, हाई-टेंशन केबल या वाटर मेन?\n\nबिना GPR स्कैन के खुदाई करने से:\n❌ लाखों की पेनल्टी\n❌ यूटिलिटी डैमेज से प्रोजेक्ट डिले\n❌ जान-माल का खतरा\n\nशाह सर्वेयर्स का GPR सिस्टम बिना गड्ढा खोदे 5 मीटर गहराई तक का 3D यूटिलिटी मैप बना देता है।\n\nसुरक्षित खुदाई के लिए आज ही स्कैन शेड्यूल करें!\n📞 +91 98222 00000\n\n#GPR #UtilityMapping #SmartCity #UndergroundScan #CivilEngineering #ShahGroup",
                "hashtags": ["#GPR", "#UtilityMapping", "#SmartCity", "#UndergroundScan", "#CivilEngineering"],
                "keywords": ["gpr survey india", "underground utility detection", "ground penetrating radar nagpur"],
                "timing": "18:00 - 19:30 IST",
                "cta": "Book GPR Scan Today"
            },
            "facebook": {
                "format": "B2B Infrastructure Risk Mitigation Case Study",
                "title": "Subsurface Utility Engineering (SUE): Mitigating Infrastructure Strikes with Dual-Frequency GPR",
                "caption": "Underground utility strikes during urban road widening, HDD crossings, or metro rail piling represent severe commercial and safety hazards. Standard utility record drawings are notoriously unreliable.\n\nShah Surveyors & Consultancy conducts CI/ASCE 38-02 Quality Level A & B Subsurface Utility Engineering using high-resolution dual-frequency GPR and electromagnetic pipe locators (EML).\n\nKey Benefits:\n1. Non-destructive detection of metallic and non-metallic utilities (PVC, HDPE, concrete, ductile iron).\n2. Millimeter-accurate depth and trajectory plotting in 3D CAD/GIS.\n3. Zero accidental disruptions to city gas or optical fiber networks.\n\nContact our SUE division for city corridor scans: +91 98222 00000",
                "hashtags": ["#SubsurfaceEngineering", "#GPRSurvey", "#SmartCityIndia", "#Trenchless", "#ShahSurveyors"],
                "keywords": ["subsurface utility engineering india", "gpr pipe detection", "smart city cable mapping"],
                "timing": "11:45 AM - 01:15 PM IST",
                "cta": "Consult SUE Specialist"
            },
            "youtube_shorts": {
                "format": "9:16 Vertical Short (40s)",
                "title": "How GPR Sees Underground Pipes Without Digging! #Shorts",
                "description": "Watch how Ground Penetrating Radar (GPR) scans underneath asphalt roads to detect gas pipes, electrical conduits, and fiber cables with millimeter accuracy. Protect your projects from costly excavation strikes with Shah Surveyors.\n\n📞 +91 98222 00000",
                "hashtags": ["#Shorts", "#GPR", "#CivilEngineering", "#Tech"],
                "keywords": ["ground penetrating radar how it works", "underground cable finder", "gpr scan in hindi"],
                "timing": "18:30 - 20:30 IST",
                "cta": "Subscribe for innovative engineering videos!"
            }
        }
    }
]

# =============================================================================
# 2. INFRA Specialized Civil Engineering Strategy Pillars (10 Pillars)
# =============================================================================
INFRA_PILLARS = [
    {
        "id": "MORTH_SECTION_300_COMPACTION",
        "service": "MoRTH Section 300 Earthwork & Embankment Engineering",
        "title": "MoRTH Section 300: Guaranteeing 98% Modified Proctor Density in Highway Embankments",
        "relevance": "Highway expansion, subgrade stabilization, and embankment testing across Central India",
        "target_audience": "Highway Concessionaires, PWD Executive Engineers, Quality Control Managers, Earthwork Subcontractors",
        "video_format": "9:16 Vertical Video / Reel",
        "duration": "38 - 45 seconds",
        "hook": "हाईवे सबग्रेड में 98% कॉम्पेक्शन अचीव करना क्यों है सबसे बड़ा चैलेंज? देखिए MoRTH Section 300 का सही तरीका।",
        "script_parts": {
            "hook": "हाईवे प्रोजेक्ट्स में अगर 98% कॉम्पेक्शन पास नहीं हुआ, तो थर्ड पार्टी QC की रिपोर्ट आते ही पूरा बिल रुक जाता है!",
            "problem": "ज्यादातर कांट्रैक्टर बिना ऑप्टिमम मॉइस्चर कंटेंट (OMC) चेक किए सिर्फ रोलर चला देते हैं, जिससे बाद में सड़क धंस जाती है।",
            "solution": "शाह इंफ्रा की टीम MoRTH Section 300 के हर क्लॉज को फॉलो करती है: प्रॉपर सैंड रिप्लेसमेंट टेस्ट, न्यूक्लियर डेंसिटी गेज और वाइब्रेटरी रोलर्स के प्रूवन पास पासिंग से 98% मॉडिफाइड प्रॉक्टर डेंसिटी की गारंटी!",
            "cta": "अपने अर्थवर्क और हाईवे सबग्रेड प्रोजेक्ट्स में जीरो-डिफेक्ट QC के लिए शाह इंफ्रा से जुड़ें।"
        },
        "shot_by_shot": [
            {"shot": 1, "visual": "Heavy vibratory soil compactor rolling over freshly spread soil embankment", "audio": "Deep diesel engine rumble + Spoken Hook", "text": "MoRTH Section 300 Compaction"},
            {"shot": 2, "visual": "QC technician pouring calibrated sand in Sand Replacement Test cylinder on site", "audio": "Explanation of field dry density vs laboratory Proctor", "text": "Sand Replacement Test (IS 2720)"},
            {"shot": 3, "visual": "Digital core density tester displaying 98.4% Relative Compaction PASSED", "audio": "Passing criteria confirmation", "text": "98.4% Proctor Density PASSED"},
            {"shot": 4, "visual": "Level, finished subgrade ready for GSB laying with Shah Infra logo", "audio": "CTA voiceover", "text": "Zero-Defect Earthwork | Shah Infra"}
        ],
        "required_footage": "Vibratory roller compaction, sand replacement testing on embankment, digital density certificate, finished smooth subgrade.",
        "voiceover": "हाईवे सबग्रेड में 98% कॉम्पेक्शन नहीं मिला तो बिल रुकना तय है। शाह इंफ्रा की टीम MoRTH Section 300 के तहत देती है 100% टेस्टेड अर्थवर्क। कॉल करें शाह ग्रुप +91 98222 00000।",
        "on_screen_text": ["MoRTH Section 300", "Sand Replacement Test", "98% Density Guaranteed", "Shah Infrastructure"],
        "cta": "Contact Shah Infra at +91 98222 00000 for certified earthwork subcontracting.",
        "thumbnail_concept": "Heavy vibratory roller with green graphic badge: '98% Proctor Density Guaranteed!'",
        "platforms": {
            "instagram": {
                "format": "9:16 Vertical Reel (40s)",
                "caption": "🚜 हाईवे और लॉजिस्टिक्स पार्क में अर्थवर्क का सबसे अहम टेस्ट: MoRTH Section 300!\n\nबिना सही कॉम्पेक्शन के बनी सड़कें पहले ही मानसून में धंस जाती हैं।\n\nशाह इंफ्रा का अर्थवर्क स्टैंडर्ड:\n✅ सैंड रिप्लेसमेंट और फील्ड डेंसिटी टेस्टिंग (IS 2720)\n✅ 98% मॉडिफाइड प्रॉक्टर डेंसिटी अचीवमेंट\n✅ ड्यूल-स्लोप ग्रेडर से प्रिसिजन लेवलिंग\n✅ डेली QC लॉग्स और लैब सर्टिफिकेशन\n\nअपने प्रोजेक्ट्स के लिए अनुभवी अर्थवर्क पार्टनर चुनें।\n\n📞 कॉल: +91 98222 00000\n\n#CivilEngineering #MoRTH #Earthwork #HighwayConstruction #Compaction #ShahGroup",
                "hashtags": ["#CivilEngineering", "#MoRTH", "#Earthwork", "#HighwayConstruction", "#Compaction"],
                "keywords": ["morth section 300 earthwork", "soil compaction test", "highway subgrade construction"],
                "timing": "18:00 - 19:30 IST",
                "cta": "DM for Earthwork Contract Inquiry"
            },
            "facebook": {
                "format": "Engineering Quality Management Article",
                "title": "MoRTH Section 300 Earthwork Protocols: Achieving 98% Relative Compaction for National Highways",
                "caption": "Subgrade failure in modern flexible pavements is almost always traceable to insufficient density control during embankment construction. Under MoRTH Section 300 specifications, top 500mm subgrade requires minimum 98% Modified Proctor Density at Optimum Moisture Content (OMC ± 1%).\n\nShah Infrastructure & Earthworks deploys heavy 12-ton vibratory compactors paired with daily Sand Replacement and Core Cutter density testing.\n\nOur Fleet & Capabilities:\n• Heavy Caterpillar Motor Graders with laser elevation receivers\n• Bomag / Hamm 12T Padfoot and Smooth Drum Vibratory Rollers\n• In-house NABL-aligned soil testing laboratory on site\n\nContact our civil works division for highway earthwork packages: +91 98222 00000",
                "hashtags": ["#CivilContractor", "#MoRTHSpecifications", "#HighwayEngineering", "#EarthworkContractor"],
                "keywords": ["morth earthwork contractor nagpur", "subgrade compaction testing", "highway embankment contractor"],
                "timing": "11:30 AM - 01:30 PM IST",
                "cta": "Inquire for Subcontracting"
            },
            "youtube_shorts": {
                "format": "9:16 Vertical Short (44s)",
                "title": "How to Pass MoRTH 98% Compaction Test! #Shorts",
                "description": "Watch how civil engineers conduct the Sand Replacement Test (IS 2720 Part 28) to verify 98% soil density on highway embankments. Shah Infrastructure delivers certified earthworks across India.\n\n📞 +91 98222 00000",
                "hashtags": ["#Shorts", "#CivilEngineering", "#MoRTH", "#Construction"],
                "keywords": ["sand replacement test", "morth section 300", "highway civil engineering"],
                "timing": "18:30 - 20:30 IST",
                "cta": "Subscribe for practical civil engineering shorts!"
            }
        }
    },
    {
        "id": "GEOTECHNICAL_SPT_FOUNDATION",
        "service": "Subsurface Soil Investigation & SPT Testing (IS 2131)",
        "title": "Subsurface Soil Investigation & Standard Penetration Test (IS 2131) for Safe Bearing Capacity",
        "relevance": "Warehouse foundations, industrial factory sheds, solar pile design, and bridge pier foundations",
        "target_audience": "Structural Engineers, Industrial Architects, Warehouse Developers, Turnkey Civil EPCs",
        "video_format": "9:16 Vertical Video / Reel",
        "duration": "35 - 42 seconds",
        "hook": "फाउंडेशन डालने से पहले अगर सॉइल टेस्टिंग में 1 गलती हुई, तो पूरी बिल्डिंग में क्रैक्स आ सकते हैं!",
        "script_parts": {
            "hook": "क्या आपको पता है कि कमजोर मिट्टी पर बनी बिल्डिंग में जब क्रैक आता है, तो उसे ठीक करने का खर्च फाउंडेशन से 5 गुना ज्यादा होता है?",
            "problem": "अक्सर लोग बिना सॉइल बेयरिंग कैपेसिटी (SBC) जाने अंदाजे से 4 फीट गड्ढा खोदकर कॉलम खड़ा कर देते हैं।",
            "solution": "शाह इंफ्रा की सॉइल इन्वेस्टिगेशन रिग्स हर 1.5 मीटर पर Standard Penetration Test (IS 2131) करती हैं और N-वैल्यू से सुरक्षित बेयरिंग कैपेसिटी (Safe SBC) कैलकुलेट करती हैं।",
            "cta": "अपनी कमर्शियल या इंडस्ट्रियल बिल्डिंग की सॉइल रिपोर्ट के लिए शाह ग्रुप से संपर्क करें।"
        },
        "shot_by_shot": [
            {"shot": 1, "visual": "Hydraulic soil drilling rig with 63.5kg hammer dropping repeatedly on split spoon sampler", "audio": "Rhythmic metal drop sound + Spoken Hook", "text": "IS 2131 Standard Penetration Test"},
            {"shot": 2, "visual": "Geotechnical engineer inspecting extracted soil core sample inside transparent core box", "audio": "Technical explanation of N-value calculation", "text": "Subsurface Strata Logging"},
            {"shot": 3, "visual": "Laboratory report chart showing Safe Bearing Capacity (SBC) curve in t/m²", "audio": "Structural safety guarantee", "text": "Safe Bearing Capacity Certified"},
            {"shot": 4, "visual": "Multi-story warehouse structure being erected safely on tested soil", "audio": "CTA voiceover", "text": "Certified Soil Testing | Shah Group"}
        ],
        "required_footage": "Geotechnical drilling rig SPT hammer drop, split spoon core sample retrieval, NABL laboratory soil report, structural warehouse construction.",
        "voiceover": "बिना सॉइल टेस्टिंग के फाउंडेशन डालना सबसे बड़ा खतरा है। शाह ग्रुप की टीम IS 2131 के तहत SPT टेस्ट करके देती है सटीक बेयरिंग कैपेसिटी। कॉल करें +91 98222 00000।",
        "on_screen_text": ["Soil Investigation IS 2131", "SPT N-Value Calculated", "Prevent Foundation Cracks", "Shah Group Soil Testing"],
        "cta": "Call +91 98222 00000 to book subsurface geotechnical soil testing.",
        "thumbnail_concept": "Soil testing drilling rig with split spoon sampler and text: 'Soil Testing Before Foundation!'",
        "platforms": {
            "instagram": {
                "format": "9:16 Vertical Reel (38s)",
                "caption": "🏗️ नींव रखने से पहले जमीन की जांच जरूरी है!\n\nकमजोर मिट्टी पर बना स्ट्रक्चर कुछ ही सालों में झुक सकता है या दीवारों में दरारें आ सकती हैं।\n\nशाह ग्रुप की जियोटेक्निकल सर्विस:\n🔬 Standard Penetration Test (IS 2131)\n🔬 सॉइल स्ट्रैटा लॉगिंग और कोर ड्रिलिंग\n🔬 सेफ बेयरिंग कैपेसिटी (SBC) कैलकुलेशन\n🔬 स्ट्रक्चरल डिजाइनर्स के लिए रेडी रिपोर्ट\n\nनागपुर और सेंट्रल इंडिया में फास्ट बोरिंग डिप्लॉयमेंट।\n\n📲 कॉल: +91 98222 00000\n\n#SoilTesting #GeotechnicalEngineering #SPT #CivilEngineering #BuildingConstruction #ShahGroup",
                "hashtags": ["#SoilTesting", "#GeotechnicalEngineering", "#SPT", "#CivilEngineering", "#BuildingConstruction"],
                "keywords": ["soil testing for building foundation", "spt test is 2131", "safe bearing capacity calculation"],
                "timing": "17:45 - 19:15 IST",
                "cta": "Book Soil Testing Today"
            },
            "facebook": {
                "format": "Structural Safety & Geotechnical Advisory",
                "title": "Subsurface Geotechnical Investigation (IS 1892 / IS 2131) for Heavy Industrial Foundations",
                "caption": "Foundation design without empirical subsurface soil mechanics data risks differential settlement, shear failure, and severe structural distress. Shah Infrastructure conducts comprehensive geotechnical borelogs tailored for structural engineers.\n\nOur Testing Protocol:\n1. Rotary core drilling up to 30m depth into hard rock.\n2. Standard Penetration Tests (SPT) conducted at 1.5m intervals as per IS 2131.\n3. Undisturbed (UDS) and disturbed soil sampling for Triaxial Shear, Direct Shear, and Atterberg limits.\n4. Calculation of Net Safe Bearing Capacity (SBC) for isolated, raft, or pile foundations.\n\nTrusted by industrial architects and developers across Maharashtra and Central India.\n\nContact our geotechnical lab: +91 98222 00000",
                "hashtags": ["#GeotechnicalTesting", "#CivilEngineering", "#FoundationDesign", "#SoilInvestigation", "#ShahGroup"],
                "keywords": ["geotechnical investigation nagpur", "soil testing lab central india", "sbc soil report"],
                "timing": "11:30 AM - 01:30 PM IST",
                "cta": "Request Soil Testing Quote"
            },
            "youtube_shorts": {
                "format": "9:16 Vertical Short (40s)",
                "title": "How SPT Soil Test Works on Construction Sites! #Shorts",
                "description": "Watch how geotechnical engineers drop a 63.5kg hammer to measure soil resistance (N-value) and calculate foundation bearing capacity as per IS 2131. Shah Group delivers certified geotechnical investigation.\n\n📞 +91 98222 00000",
                "hashtags": ["#Shorts", "#SoilTesting", "#CivilEngineering", "#Construction"],
                "keywords": ["spt test demonstration", "standard penetration test in hindi", "foundation soil testing"],
                "timing": "18:30 - 20:30 IST",
                "cta": "Subscribe for real site testing videos!"
            }
        }
    }
]


# =============================================================================
# 3. Dynamic Non-Repeating Marketing Strategy Engine
# =============================================================================
def get_recently_used_pillars(store: Store, workspace_id: str, limit: int = 10) -> List[str]:
    """Retrieves list of recently used strategy pillars to prevent repetition."""
    rows = store.fetchall(
        "SELECT service_pillar FROM ai_marketing_briefs WHERE workspace_id=? AND service_pillar IS NOT NULL AND service_pillar != '' ORDER BY id DESC LIMIT ?",
        (workspace_id, limit)
    )
    return [r["service_pillar"] for r in rows if r.get("service_pillar")]


def select_non_repeating_pillar(store: Store, workspace_id: str) -> Dict[str, Any]:
    """Selects an unused or least recently used pillar based on history and day-of-week."""
    all_pillars = INFRA_PILLARS if workspace_id == "INFRA" else SSC_PILLARS
    recent_pillar_ids = get_recently_used_pillars(store, workspace_id, limit=len(all_pillars) - 1)

    # Filter out recently used pillars
    available = [p for p in all_pillars if p["id"] not in recent_pillar_ids]
    if not available:
        # If all have been used, pick the one used furthest back in time
        available = all_pillars

    # Deterministic rotation based on current day of year so repeat calls on the same day stay consistent,
    # but subsequent days advance smoothly
    day_of_year = now_kolkata().timetuple().tm_yday
    selected_pillar = available[day_of_year % len(available)]
    return selected_pillar


def generate_daily_marketing_brief(store: Store, workspace_id: str, force_fresh: bool = False) -> Dict[str, Any]:
    """Generates an authentic, non-repeating daily marketing strategy for SSC or INFRA.
    
    Includes:
    - Service to promote & relevance reason
    - Video format, duration, spoken opening hook
    - Full dual-language video script (Hindi + English)
    - 4-part shot-by-shot visual instructions & required footage
    - High-converting CTA and thumbnail concept
    - Platform-specific publishing strategies for Instagram, Facebook, and YouTube Shorts.
    """
    today_str = now_kolkata_date()
    
    # Check if brief already exists today unless force_fresh is requested
    if not force_fresh:
        existing = store.fetchone(
            "SELECT * FROM ai_marketing_briefs WHERE workspace_id=? AND brief_date=? ORDER BY id DESC LIMIT 1",
            (workspace_id, today_str)
        )
        if existing and existing.get("platform_campaigns_json"):
            res = dict(existing)
            res["platform_campaigns"] = json.loads(res.get("platform_campaigns_json") or "{}")
            res["video_script"] = json.loads(res.get("video_script_json") or "{}")
            res["shot_by_shot"] = json.loads(res.get("shot_by_shot_json") or "[]")
            return res

    pillar = select_non_repeating_pillar(store, workspace_id)

    # Build structured marketing concepts
    industry_trends = (
        f"Verified Industry Trend: {pillar['relevance']}. High market demand for certified precision "
        f"in {pillar['service']}. Contractors and developers require documented compliance."
    )
    competitor_insights = (
        "Competitors predominantly publish static completed site photos without demonstrating technical precision. "
        "Short-form video demonstrations displaying real-time digital sensor readouts and accuracy tolerances "
        "consistently achieve 3.8x to 4.5x higher engagement and immediate B2B lead inquiries."
    )
    recommended_posts = (
        f"1. **Instagram / Facebook Video Reel**: '{pillar['hook']}'\n"
        f"2. **Facebook / LinkedIn Technical Case Study**: '{pillar['platforms']['facebook']['title']}'\n"
        f"3. **YouTube Short**: '{pillar['platforms']['youtube_shorts']['title']}'"
    )
    reel_ideas = f"{pillar['shot_by_shot'][0]['visual']} transitioning into {pillar['shot_by_shot'][1]['visual']}."
    posting_schedule = (
        f"• **Instagram**: {pillar['platforms']['instagram']['timing']}\n"
        f"• **Facebook**: {pillar['platforms']['facebook']['timing']}\n"
        f"• **YouTube Shorts**: {pillar['platforms']['youtube_shorts']['timing']}"
    )

    cur = store.conn.execute(
        """INSERT INTO ai_marketing_briefs (
            workspace_id, brief_date, industry_trends, competitor_insights,
            recommended_posts, reel_ideas, platform_recommendations, posting_schedule,
            target_audience, cta_objective, platform_campaigns_json, video_script_json,
            shot_by_shot_json, service_pillar, hook_text, relevance_reason, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
        (
            workspace_id, today_str, industry_trends, competitor_insights,
            recommended_posts, reel_ideas, "Instagram, Facebook, YouTube Shorts",
            posting_schedule, pillar["target_audience"], pillar["cta"],
            json.dumps(pillar["platforms"]),
            json.dumps(pillar["script_parts"]),
            json.dumps(pillar["shot_by_shot"]),
            pillar["id"], pillar["hook"], pillar["relevance"]
        )
    )
    store.conn.commit()
    brief_id = cur.lastrowid
    row = store.fetchone("SELECT * FROM ai_marketing_briefs WHERE id=?", (brief_id,))
    res = dict(row)
    res["platform_campaigns"] = pillar["platforms"]
    res["video_script"] = pillar["script_parts"]
    res["shot_by_shot"] = pillar["shot_by_shot"]
    return res


def save_brief_to_content_calendar(store: Store, workspace_id: str, brief_id: int, platform: str = "instagram") -> Dict[str, Any]:
    """Saves a daily marketing strategy directly into the Content Calendar as a user-approved draft."""
    brief = store.fetchone("SELECT * FROM ai_marketing_briefs WHERE id=?", (brief_id,))
    if not brief:
        raise ValueError(f"Brief ID {brief_id} not found.")

    platforms = json.loads(brief.get("platform_campaigns_json") or "{}")
    p_data = platforms.get(platform) or platforms.get("instagram", {})
    scripts = json.loads(brief.get("video_script_json") or "{}")

    title = p_data.get("title") or brief.get("hook_text") or "Strategic Daily AI Campaign"
    caption = p_data.get("caption") or brief.get("recommended_posts")
    hashtags = json.dumps(p_data.get("hashtags", []))
    keywords = json.dumps(p_data.get("keywords", []))
    full_script = f"Hook: {scripts.get('hook', '')}\n\nProblem: {scripts.get('problem', '')}\n\nSolution: {scripts.get('solution', '')}\n\nCTA: {scripts.get('cta', '')}"

    cur = store.conn.execute(
        """INSERT INTO social_content_items (
            workspace_id, platform, content_format, hook, key_message, cta,
            keywords, title, script, caption, voiceover_text,
            visual_direction, status, created_at, updated_at
        ) VALUES (?, ?, 'reel', ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)""",
        (
            workspace_id, platform, brief.get("hook_text", ""),
            brief.get("industry_trends", ""), brief.get("cta_objective", ""),
            keywords, title, full_script, caption,
            scripts.get("solution", ""), brief.get("reel_ideas", ""),
            now_kolkata_iso(), now_kolkata_iso()
        )
    )
    store.conn.commit()
    content_id = cur.lastrowid
    return {
        "ok": True,
        "content_id": content_id,
        "status": "draft",
        "message": f"Strategy successfully saved to Content Calendar for {platform.title()}."
    }
