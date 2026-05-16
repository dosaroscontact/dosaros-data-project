# API Microservices Architecture

**Date:** 2026-05-16  
**Scope:** DOS Aros Landing Page Backend  
**Pattern:** Mock → Real API Swap (Zero-Code Switch)

---

## Philosophy

**Design for swappability from day 1.**

Current reality:
- Don't have all data sources (Liga ACB, FIBA have no public/documented APIs)
- Want to launch landing TODAY
- Want to add real data LATER without refactoring

Solution: **Mock Data Microservices**
- Each endpoint returns same shape as "real" API
- Mock data = predictable, fake but realistic
- When real API available, only change the data source, not the contract

---

## Architecture

```
┌────────────────────────────────────────┐
│         Next.js Landing (Vercel)       │
├────────────────────────────────────────┤
│                                        │
│  GET  /api/live-scores                │
│  GET  /api/upcoming                   │
│  GET  /api/events                     │
│  POST /api/query                      │
│                                        │
└────────────────────────────────────────┘
              ↓                 ↓
    ┌─────────────────┐  ┌──────────────┐
    │ Mock Data Layer │  │ Pi Backend   │
    │ (swap point)    │  │ (prod)       │
    │                 │  │              │
    │ /mock/live.ts   │  │ /api/query   │
    │ /mock/upcoming.ts│ │  → NL→SQL    │
    │ /mock/events.ts │  │  → DB/AI     │
    └─────────────────┘  └──────────────┘
```

---

## Endpoints

### 1. GET `/api/live-scores`

**Purpose:** Real-time match scores  
**Response Time:** <100ms (cached, refreshed every 30-60s)

**Shape:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-05-16T14:32:00Z",
    "leagues": {
      "nba": [
        {
          "id": "nba_2024_lal_bos_001",
          "league": "NBA",
          "game_date": "2026-05-16",
          "home_team": {
            "code": "LAL",
            "name": "Los Angeles Lakers",
            "logo": "https://...lakers.png",
            "score": 98
          },
          "away_team": {
            "code": "BOS",
            "name": "Boston Celtics",
            "logo": "https://...celtics.png",
            "score": 102
          },
          "period": 3,
          "time_remaining": "4:23",
          "status": "live", // "live" | "scheduled" | "final"
          "updated_at": "2026-05-16T14:32:00Z"
        }
      ],
      "euroleague": [...],
      "liga_acb": [...],
      "wnba": [...],
      "fiba": [...]
    }
  }
}
```

**Mock Implementation** (`src/api/mock/live-scores.ts`):
```typescript
export function getMockLiveScores() {
  return {
    success: true,
    data: {
      timestamp: new Date().toISOString(),
      leagues: {
        nba: [
          {
            id: "nba_2024_lal_bos_001",
            league: "NBA",
            home_team: { code: "LAL", name: "Lakers", score: 98 },
            away_team: { code: "BOS", name: "Celtics", score: 102 },
            period: 3,
            time_remaining: "4:23",
            status: "live",
            updated_at: new Date().toISOString()
          }
        ],
        euroleague: [...],
        // ... other leagues
      }
    }
  }
}
```

**Real Implementation** (future):
- Fetch from NBA API → transform to shape
- Fetch from EuroLeague API → transform to shape
- Fetch from Liga ACB (web scraping) → transform
- Same return shape, different source

---

### 2. GET `/api/upcoming`

**Purpose:** Next scheduled games  
**Response Time:** <100ms (cached, updated daily at midnight)

**Shape:**
```json
{
  "success": true,
  "data": {
    "featured": [
      {
        "id": "nba_2024_gsw_lal_001",
        "league": "NBA",
        "game_date": "2026-05-17",
        "game_time": "19:30Z",
        "home_team": { "code": "GSW", "name": "Golden State Warriors" },
        "away_team": { "code": "LAL", "name": "Los Angeles Lakers" },
        "is_playoff": true,
        "series_status": "1-1" // if playoff
      }
    ]
  }
}
```

**Mock:** Hardcoded next 3-4 matches  
**Real:** Query ESPN/NBA API for scheduled games

---

### 3. GET `/api/events`

**Purpose:** Latest highlights, playoff updates  
**Response Time:** <100ms (cache, updated hourly)

**Shape:**
```json
{
  "success": true,
  "data": [
    {
      "id": "event_2024_001",
      "type": "playoff_series_update",
      "league": "NBA",
      "title": "Lakers lead series 3-1 against Celtics (Game 5 tonight)",
      "summary": "LeBron had 28 pts in Game 4 as LAL took commanding lead.",
      "teams": ["LAL", "BOS"],
      "image": "https://...game4.jpg",
      "created_at": "2026-05-16T10:00:00Z"
    }
  ]
}
```

**Mock:** Hardcoded 3 recent events  
**Real:** Query DOS Aros `insight_generator.py` for perlas + playoff status

---

### 4. POST `/api/query`

**Purpose:** NL→Data query  
**Request:**
```json
{
  "query": "¿Cuántos puntos promedió LeBron en 2024?",
  "language": "es"
}
```

**Response:**
```json
{
  "success": true,
  "result": "LeBron James promedió 25.3 puntos en temporada 2023-24.",
  "source": "db", // "db" | "ai" | "error"
  "query_time_ms": 1240,
  "model": "sqlite", // if db
  "confidence": 0.95 // if ai
}
```

**Flow:**
1. POST → Next.js `/api/query` handler
2. Handler → `POST /query` to Pi backend
3. Pi: Try SQLite first, fallback to AI
4. Return to Next.js → client

**Backend (Pi):**
```python
# src/app/api/query.py (hypothetical)
@app.post("/api/query")
def query(request):
    nl_query = request.json["query"]
    
    # Try database
    result = analista_ia.query_db(nl_query)
    if result:
        return {
            "success": True,
            "result": result,
            "source": "db",
            "query_time_ms": timer_ms
        }
    
    # Fallback to AI
    ai_result = api_manager.query_ai(nl_query)
    return {
        "success": True,
        "result": ai_result,
        "source": "ai",
        "query_time_ms": timer_ms
    }
```

---

## Live Scores Refresh Strategy

**On Landing Page:**
1. Load page → GET `/api/live-scores` (get current state)
2. Page renders ticker
3. Every 30-60s: Polling refresh (GET `/api/live-scores`)
4. New data → re-render ticker smoothly (Framer Motion)

**Cron on Pi:**
- 9:00 AM daily: Fetch all games scheduled for TODAY
- For each game: Check start time
- T-5min: Start polling NBA/Euro/Liga APIs
- T+start to T+3h: Active polling every 30s
- T+end: Stop polling, mark final

**Result:** Zero real-time WebSocket, simple polling, works on free Vercel tier.

---

## The Swap (Mock → Real)

**Current Code:**
```typescript
// src/api/route.ts
export async function GET(request) {
  const data = getMockLiveScores(); // ← Mock
  return Response.json(data);
}
```

**When Real API Ready:**
```typescript
// src/api/route.ts
export async function GET(request) {
  const data = await getRealLiveScores(); // ← Real (same shape)
  return Response.json(data);
}
```

**No frontend changes needed.** Same response shape, different source.

---

## Error Handling

**If real API fails:**
```json
{
  "success": false,
  "error": "Unable to fetch live scores",
  "fallback": "mock", // Show mock data as placeholder
  "message": "Showing example data. Real scores coming soon."
}
```

---

## Directory Structure

```
src/
├── api/
│   ├── mock/
│   │   ├── live-scores.ts      ← Mock data generator
│   │   ├── upcoming.ts
│   │   └── events.ts
│   ├── route.ts                ← Endpoints
│   └── query.ts
├── components/
│   ├── LiveScoresTicker.tsx
│   ├── QueryBox.tsx
│   └── ...
└── lib/
    └── api-client.ts           ← Shared fetch logic
```

---

## Testing

**Unit tests (mock data):**
```typescript
test("getMockLiveScores returns valid shape", () => {
  const data = getMockLiveScores();
  expect(data.success).toBe(true);
  expect(data.data.leagues.nba).toBeArray();
});
```

**E2E tests (with real API):**
```typescript
test("GET /api/live-scores returns same shape as mock", async () => {
  const res = await fetch("/api/live-scores");
  const data = await res.json();
  expect(data.data.leagues).toBeDefined();
});
```

---

## Links

- [[Landing Page Architecture]] — Overall design
- [[API Documentation (DOS Aros)]] — Detailed endpoint specs
