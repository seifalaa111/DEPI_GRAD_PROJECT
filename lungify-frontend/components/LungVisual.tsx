"use client";

import { motion } from "framer-motion";

export function LungVisual() {
  return (
    <div className="lung-visual" aria-hidden="true">
      <svg
        className="lung-svg"
        viewBox="0 0 460 460"
        role="img"
      >
        <defs>
          <radialGradient id="lungGlow" cx="50%" cy="52%" r="54%">
            <stop offset="0%" stopColor="#B9E7D0" stopOpacity="0.34" />
            <stop offset="70%" stopColor="#3DAFC2" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#3DAFC2" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="lungFill" x1="90" x2="370" y1="160" y2="370">
            <stop offset="0%" stopColor="#B9E7D0" stopOpacity="0.52" />
            <stop offset="100%" stopColor="#EAF7FA" stopOpacity="0.74" />
          </linearGradient>
        </defs>

        <circle cx="230" cy="262" r="170" fill="url(#lungGlow)" />

        <motion.g
          className="lung-breath-group"
          animate={{ scale: [1, 1.035, 1], opacity: [0.88, 1, 0.88] }}
          transition={{ duration: 3.2, repeat: Infinity, ease: "easeInOut" }}
          style={{ originX: "50%", originY: "58%" }}
        >
          <path
            className="lung-lobe"
            d="M216 178 C201 155 175 145 146 151 C112 158 89 190 80 238 C69 297 85 343 120 365 C149 383 181 373 202 343 C217 321 223 288 222 250 C222 219 223 195 216 178 Z"
          />
          <path
            className="lung-lobe"
            d="M244 176 C262 151 291 145 322 153 C358 162 382 199 390 249 C400 313 373 363 328 376 C292 386 261 364 248 323 C237 287 233 222 244 176 Z"
          />
          <path
            className="lung-inner-edge"
            d="M216 195 C206 224 204 254 209 289 C213 319 204 344 186 360"
          />
          <path
            className="lung-inner-edge"
            d="M244 196 C253 225 255 257 249 291 C244 321 254 350 279 366"
          />
          <path
            className="lung-fissure"
            d="M112 252 C143 246 174 263 199 299"
          />
          <path
            className="lung-fissure"
            d="M348 253 C316 246 287 263 262 302"
          />
        </motion.g>

        <g className="bronchial-tree">
          <path d="M230 118 C230 133 230 146 230 158" className="airway airway-main" />
          <path d="M230 158 C219 174 205 187 188 199" className="airway airway-main" />
          <path d="M230 158 C243 174 258 188 275 202" className="airway airway-main" />

          <path d="M188 199 C170 214 158 232 151 253" className="airway airway-branch" />
          <path d="M181 211 C163 213 146 222 133 236" className="airway airway-branch" />
          <path d="M164 239 C147 250 136 267 130 287" className="airway airway-small" />
          <path d="M158 255 C173 269 181 288 184 310" className="airway airway-small" />
          <path d="M194 216 C205 231 210 249 210 270" className="airway airway-small" />

          <path d="M275 202 C295 218 309 238 317 261" className="airway airway-branch" />
          <path d="M282 214 C301 217 318 228 332 244" className="airway airway-branch" />
          <path d="M303 246 C323 258 337 277 344 300" className="airway airway-small" />
          <path d="M316 264 C301 279 294 298 292 320" className="airway airway-small" />
          <path d="M267 219 C256 235 251 253 252 273" className="airway airway-small" />
        </g>

        <motion.path
          className="ct-sweep"
          d="M70 232 C130 222 176 232 221 229 C271 226 319 235 390 226"
          animate={{ y: [-122, 126], opacity: [0, 0.58, 0] }}
          transition={{ duration: 3.8, repeat: Infinity, ease: "easeInOut" }}
        />
      </svg>
    </div>
  );
}
