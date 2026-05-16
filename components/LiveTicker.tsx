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
  competition: string
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
    competition: 'NBA',
    league: 'NBA',
  },
  {
    id: '2',
    homeTeam: 'Real Madrid',
    awayTeam: 'Barcelona',
    homeScore: 78,
    awayScore: 75,
    period: '3Q',
    competition: 'Liga ACB',
    league: 'ACB',
  },
  {
    id: '3',
    homeTeam: 'Partizan',
    awayTeam: 'Fenerbahçe',
    homeScore: 68,
    awayScore: 72,
    period: 'Final',
    competition: 'EuroLeague',
    league: 'EuroLeague',
  },
  {
    id: '4',
    homeTeam: 'Boston',
    awayTeam: 'Miami',
    homeScore: 95,
    awayScore: 92,
    period: '3Q 6:12',
    competition: 'NBA',
    league: 'NBA',
  },
]

export default function LiveTicker() {
  const [games, setGames] = useState<GameScore[]>(MOCK_GAMES)
  const [selectedGame, setSelectedGame] = useState<string | null>(null)

  useEffect(() => {
    const interval = setInterval(() => {
      setGames((prev) =>
        prev.map((game) => ({
          ...game,
          homeScore: Math.max(game.homeScore, Math.random() > 0.7 ? game.homeScore + 1 : game.homeScore),
          awayScore: Math.max(game.awayScore, Math.random() > 0.7 ? game.awayScore + 1 : game.awayScore),
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

  return (
    <section className="w-full py-12 sm:py-16 md:py-20 px-4 sm:px-6 bg-dos-white">
      <div className="max-w-6xl mx-auto">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-3xl sm:text-4xl font-heading font-bold text-dos-blue mb-8 text-center"
        >
          Partidos en vivo
        </motion.h2>

        {/* Desktop: Horizontal scroll */}
        <div className="hidden md:flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide">
          {games.map((game, idx) => (
            <motion.div
              key={game.id}
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.1 }}
              viewport={{ once: true }}
              className="flex-shrink-0 w-80 snap-center"
            >
              <GameCard game={game} isSelected={selectedGame === game.id} onSelect={setSelectedGame} leagueColor={leagueColors[game.league]} />
            </motion.div>
          ))}
        </div>

        {/* Mobile: Vertical stack */}
        <div className="md:hidden space-y-3">
          {games.map((game, idx) => (
            <motion.div
              key={game.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.1 }}
              viewport={{ once: true }}
            >
              <GameCard game={game} isSelected={selectedGame === game.id} onSelect={setSelectedGame} leagueColor={leagueColors[game.league]} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

interface GameCardProps {
  game: GameScore
  isSelected: boolean
  onSelect: (id: string) => void
  leagueColor: string
}

function GameCard({ game, isSelected, onSelect, leagueColor }: GameCardProps) {
  return (
    <motion.button
      onClick={() => onSelect(game.id)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`w-full p-4 rounded-lg border-2 transition-all duration-300 text-left cursor-pointer active:scale-95 min-h-[120px] sm:min-h-[100px] flex flex-col justify-between ${
        isSelected
          ? 'border-dos-orange bg-dos-orange/10'
          : 'border-dos-gray bg-dos-white hover:border-dos-orange/50'
      }`}
      aria-label={`${game.homeTeam} vs ${game.awayTeam} - ${game.period}`}
      aria-pressed={isSelected}
    >
      <div className="flex items-center justify-between mb-2">
        <span className={`${leagueColor} text-dos-white px-2 py-1 rounded text-xs font-bold`}>
          {game.league}
        </span>
        <span className="text-xs font-body text-dos-gray-dark">{game.period}</span>
      </div>

      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex-1 text-sm font-heading font-bold text-dos-blue truncate">
          {game.homeTeam}
        </div>
        <div className="text-lg font-heading font-bold text-dos-orange">
          {game.homeScore}
        </div>
      </div>

      <div className="flex items-center justify-between gap-3">
        <div className="flex-1 text-sm font-heading font-bold text-dos-blue truncate">
          {game.awayTeam}
        </div>
        <div className="text-lg font-heading font-bold text-dos-orange">
          {game.awayScore}
        </div>
      </div>
    </motion.button>
  )
}
