'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface GameScore {
  id: string
  homeTeam: string
  awayTeam: string
  homeScore: number
  awayScore: number
  period: string
  league: 'NBA' | 'WNBA' | 'EuroLeague' | 'ACB' | 'FIBA'
}

const MOCK_GAMES: GameScore[] = [
  {
    id: '1',
    homeTeam: 'LAL',
    awayTeam: 'GSW',
    homeScore: 112,
    awayScore: 108,
    period: '4Q 3:45',
    league: 'NBA',
  },
  {
    id: '2',
    homeTeam: 'Boston',
    awayTeam: 'Miami',
    homeScore: 95,
    awayScore: 92,
    period: '3Q 6:12',
    league: 'NBA',
  },
  {
    id: '3',
    homeTeam: 'Real Madrid',
    awayTeam: 'Barcelona',
    homeScore: 78,
    awayScore: 75,
    period: '3Q',
    league: 'ACB',
  },
  {
    id: '4',
    homeTeam: 'Partizan',
    awayTeam: 'Fenerbahçe',
    homeScore: 68,
    awayScore: 72,
    period: 'Final',
    league: 'EuroLeague',
  },
]

export default function StickyTicker() {
  const [games, setGames] = useState<GameScore[]>(MOCK_GAMES)

  useEffect(() => {
    const interval = setInterval(() => {
      setGames((prev) =>
        prev.map((game) => ({
          ...game,
          homeScore: Math.max(game.homeScore, Math.random() > 0.8 ? game.homeScore + 1 : game.homeScore),
          awayScore: Math.max(game.awayScore, Math.random() > 0.8 ? game.awayScore + 1 : game.awayScore),
        }))
      )
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const leagueColors: Record<GameScore['league'], string> = {
    NBA: 'bg-red-600',
    WNBA: 'bg-blue-600',
    EuroLeague: 'bg-purple-600',
    ACB: 'bg-yellow-600',
    FIBA: 'bg-green-600',
  }

  const scroll = (direction: 'left' | 'right') => {
    const container = document.getElementById('ticker-scroll')
    if (container) {
      const scrollAmount = 300
      container.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      })
    }
  }

  return (
    <div className="sticky top-[60px] sm:top-[72px] z-40 bg-dos-blue/95 dark:bg-dos-blue-dark/95 backdrop-blur-md border-b border-dos-magenta/20 shadow-md">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-3">
        {/* Live badge */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-2 h-2 bg-dos-orange rounded-full animate-pulse"></div>
          <span className="text-xs font-heading font-bold text-dos-orange uppercase whitespace-nowrap">
            EN VIVO
          </span>
        </div>

        {/* Divider */}
        <div className="hidden sm:block w-px h-6 bg-dos-magenta/30"></div>

        {/* Scroll container */}
        <div className="relative flex-1 overflow-hidden">
          <div
            id="ticker-scroll"
            className="flex gap-3 overflow-x-auto scrollbar-hide scroll-smooth"
          >
            {games.map((game) => (
              <motion.div
                key={game.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex-shrink-0 bg-dos-blue/50 hover:bg-dos-blue/70 border border-dos-magenta/30 rounded-lg px-3 py-2 cursor-pointer transition-all duration-300 group"
              >
                <div className="flex items-center gap-2">
                  <span className={`${leagueColors[game.league]} text-dos-white px-1.5 py-0.5 rounded text-xs font-bold whitespace-nowrap`}>
                    {game.league}
                  </span>
                  <div className="text-dos-white text-xs font-heading font-bold whitespace-nowrap group-hover:text-dos-orange transition-colors">
                    <span>{game.homeTeam}</span>
                    <span className="text-dos-orange mx-1">{game.homeScore}</span>
                    <span>-</span>
                    <span className="text-dos-orange mx-1">{game.awayScore}</span>
                    <span>{game.awayTeam}</span>
                  </div>
                  <span className="text-dos-gray text-xs whitespace-nowrap">{game.period}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Navigation buttons */}
        <div className="hidden sm:flex items-center gap-2 flex-shrink-0">
          <button
            onClick={() => scroll('left')}
            className="p-1.5 hover:bg-dos-magenta/20 rounded-lg transition-colors text-dos-orange"
            aria-label="Scroll left"
          >
            ←
          </button>
          <button
            onClick={() => scroll('right')}
            className="p-1.5 hover:bg-dos-magenta/20 rounded-lg transition-colors text-dos-orange"
            aria-label="Scroll right"
          >
            →
          </button>
        </div>
      </div>
    </div>
  )
}
