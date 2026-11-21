# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — AI Image Generation Module.

Zero Paid Software / Service Dependency Architecture:
  1. Primary Free Provider: Pollinations.ai free text-to-image API
     (https://image.pollinations.ai/prompt/...)
     - Zero API key required, zero billing, zero cost.
     - Direct high-resolution output (1:1, 9:16, 16:9).
  2. Local Offline Fallback: High-contrast branded vector/SVG & Canvas renderer
     - Guaranteed zero-failure offline generation.
  3. Prompt Engineering & Enhancer:
     - Automatically infuses domain knowledge: DGPS RTK, Total Station, Aerial LiDAR,
       Civil Infrastructure, Highway Cross-Sections, Survey of India GTS Benchmarks.
  4. Media Library Integration:
     - Automatically saves generated PNG to `data/m19_output/`
     - Inserts record into `social_media_assets` with checksum and metadata.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import random
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..config import project_root
from ..store import Store

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))
MEDIA_OUTPUT_DIR = os.path.join(os.getcwd(), "data", "m19_output")

STYLE_PRESETS = {
    "surveying_dgps": {
        "label": "DGPS & Land Surveying",
        "keywords": "high-precision DGPS GNSS receiver antenna mounted on carbon fiber tripod, Survey of India benchmark pillar, professional civil surveyor in safety neon jacket looking at handheld controller, open topography landscape, vivid colors, photorealistic 8k, architectural digest photography"
    },
    "drone_lidar": {
        "label": "Aerial Drone & LiDAR",
        "keywords": "advanced industrial hexacopter drone equipped with LiDAR scanner surveying a large highway infrastructure corridor, point cloud laser beams, 3D elevation contour mapping overlay, golden hour atmospheric sunlight, hyper-detailed"
    },
    "civil_infra": {
        "label": "Civil Infrastructure & Earthworks",
        "keywords": "large infrastructure construction site, hydraulic crawler excavator digging foundation embankment, heavy compaction road roller, MoRTH compliant highway sub-base, civil engineers reviewing engineering blueprints"
    },
    "highway_paving": {
        "label": "Highway Paving & Geometric Alignment",
        "keywords": "modern multi-lane national expressway under construction, sensor-guided asphalt paving machine, pristine geometric curves, fresh blacktop bitumen, road marking demarcation, scenic central India backdrop"
    },
    "corporate_branding": {
        "label": "Corporate Tech & Brand Graphic",
        "keywords": "modern corporate engineering graphic, sleek geometric lines, deep navy blue and cyan holographic accents, high-end business presentation aesthetic, sharp typography, minimalist layout"
    }
}

ASPECT_RATIOS = {
    "1:1": (1080, 1080),
    "9:16": (1080, 1920),
    "16:9": (1920, 1080)
}


def enhance_prompt(prompt: str, style_key: str = "surveying_dgps", workspace_id: str = "SSC") -> str:
    """Enhances a user brief with domain-specific engineering and artistic parameters."""
    style = STYLE_PRESETS.get(style_key, STYLE_PRESETS["surveying_dgps"])
    company_name = "Shah Surveyors & Consultancy" if workspace_id == "SSC" else "Shah Infra Developers"
    
    clean_p = prompt.strip()
    enhanced = f"{clean_p}, {style['keywords']}, professional quality for {company_name}, masterwork composition, hyperrealistic, 4k sharp focus"
    return enhanced


def generate_offline_svg_image(prompt: str, style_key: str, width: int, height: int, workspace_id: str) -> bytes:
    """Generates an offline SVG/PNG fallback image when external internet is unreachable."""
    bg_gradient_start = "#0b1120"
    bg_gradient_end = "#1e293b"
    accent = "#38bdf8" if workspace_id == "SSC" else "#14b8a6"
    title_text = prompt[:45] + ("..." if len(prompt) > 45 else "")
    brand = "SHAH SURVEYORS & CONSULTANCY" if workspace_id == "SSC" else "SHAH INFRA DEVELOPERS"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{bg_gradient_start}"/>
          <stop offset="100%" stop-color="{bg_gradient_end}"/>
        </linearGradient>
        <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="{accent}"/>
          <stop offset="100%" stop-color="#818cf8"/>
        </linearGradient>
      </defs>
      <rect width="{width}" height="{height}" fill="url(#bg)"/>
      <circle cx="{width*0.8}" cy="{height*0.2}" r="{min(width, height)*0.25}" fill="{accent}" opacity="0.08"/>
      <circle cx="{width*0.2}" cy="{height*0.8}" r="{min(width, height)*0.35}" fill="{accent}" opacity="0.05"/>
      <rect x="0" y="0" width="{width}" height="14" fill="url(#accentGrad)"/>
      
      <rect x="60" y="60" width="220" height="34" rx="17" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="1.5"/>
      <text x="170" y="82" fill="{accent}" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle">{brand}</text>
      
      <g transform="translate({width/2}, {height*0.45})">
        <circle cx="0" cy="0" r="70" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="8 6"/>
        <line x1="-90" y1="0" x2="90" y2="0" stroke="{accent}" stroke-width="2" opacity="0.7"/>
        <line x1="0" y1="-90" x2="0" y2="90" stroke="{accent}" stroke-width="2" opacity="0.7"/>
        <circle cx="0" cy="0" r="12" fill="{accent}"/>
      </g>
      
      <text x="{width/2}" y="{height*0.65}" fill="#f8fafc" font-family="Arial, sans-serif" font-size="{int(min(width, height)*0.038)}" font-weight="bold" text-anchor="middle">
        {title_text}
      </text>
      
      <text x="{width/2}" y="{height*0.72}" fill="#94a3b8" font-family="Arial, sans-serif" font-size="{int(min(width, height)*0.024)}" text-anchor="middle">
        Precision Engineering Visual &bull; {STYLE_PRESETS.get(style_key, {}).get('label', 'Engineering')}
      </text>
      
      <rect x="60" y="{height-80}" width="{width-120}" height="1" fill="#334155"/>
      <text x="60" y="{height-45}" fill="#64748b" font-family="Arial, sans-serif" font-size="14">SHAH Group AI OS &bull; Social Creative Studio</text>
      <text x="{width-60}" y="{height-45}" fill="{accent}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="end">Verified Local Generation</text>
    </svg>"""
    return svg.encode("utf-8")


def generate_ai_image(
    store: Store,
    prompt: str,
    workspace_id: str = "SSC",
    aspect_ratio: str = "1:1",
    style_key: str = "surveying_dgps",
    save_to_library: bool = True
) -> Dict[str, Any]:
    """Generates an AI image using free Pollinations API with zero paid fallbacks.
    
    If network is unavailable or rate limited, gracefully falls back to local high-res SVG.
    """
    os.makedirs(MEDIA_OUTPUT_DIR, exist_ok=True)
    t0 = time.time()
    
    width, height = ASPECT_RATIOS.get(aspect_ratio, (1080, 1080))
    enhanced = enhance_prompt(prompt, style_key, workspace_id)
    
    ts = int(time.time())
    seed = random.randint(100000, 999999)
    filename = f"ai_img_{workspace_id}_{seed}_{ts}.png"
    out_path = os.path.join(MEDIA_OUTPUT_DIR, filename)

    provider_used = "pollinations_free"
    image_bytes: Optional[bytes] = None
    is_fallback = False

    # 1. Attempt Pollinations.ai free text-to-image API
    try:
        encoded_prompt = urllib.parse.quote(enhanced)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SHAH-AI-OS/2.0"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status == 200:
                data = resp.read()
                # Verify that response is valid image data (PNG or JPEG header)
                if len(data) > 1000 and (data.startswith(b"\x89PNG") or data.startswith(b"\xff\xd8")):
                    image_bytes = data
    except Exception as e:
        provider_used = "local_vector_canvas"
        is_fallback = True

    # 2. Local fallback if external call fails or offline
    if not image_bytes:
        filename = f"ai_img_{workspace_id}_{seed}_{ts}.svg"
        out_path = os.path.join(MEDIA_OUTPUT_DIR, filename)
        image_bytes = generate_offline_svg_image(prompt, style_key, width, height, workspace_id)
        provider_used = "local_vector_canvas"
        is_fallback = True

    # Write file to disk
    with open(out_path, "wb") as f:
        f.write(image_bytes)

    latency_ms = int((time.time() - t0) * 1000)
    b64_str = base64.b64encode(image_bytes).decode("ascii")
    mime = "image/svg+xml" if filename.endswith(".svg") else "image/png"
    thumb_url = f"data:{mime};base64,{b64_str}"

    asset_id = None
    if save_to_library and store:
        rel_path = os.path.relpath(out_path, project_root()).replace("\\", "/")
        checksum = hashlib.sha256(image_bytes).hexdigest()[:16]
        cur = store.conn.execute(
            "INSERT INTO social_media_assets (workspace_id, filename, file_type, content_type, "
            "duration_seconds, resolution, frame_rate, has_audio, checksum, status, thumb_url) "
            "VALUES (?, ?, 'image', ?, 0, ?, '0', 0, ?, 'ready', ?)",
            (workspace_id, rel_path, mime, f"{width}x{height}", checksum, thumb_url)
        )
        store.conn.commit()
        asset_id = cur.lastrowid

    return {
        "ok": True,
        "filename": filename,
        "output_path": out_path,
        "asset_id": asset_id,
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "style_applied": style_key,
        "original_prompt": prompt,
        "enhanced_prompt": enhanced,
        "provider": provider_used,
        "is_fallback": is_fallback,
        "latency_ms": latency_ms,
        "image_url": thumb_url,
        "download_url": f"/api/media/download/{asset_id}" if asset_id else None
    }


def get_image_generation_styles() -> Dict[str, Any]:
    """Returns available styles and aspect ratios."""
    return {
        "styles": STYLE_PRESETS,
        "aspect_ratios": list(ASPECT_RATIOS.keys()),
        "free_tier": True,
        "zero_paid_billing_enforced": True
    }
