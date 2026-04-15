'use client';

import { useEffect, useRef } from 'react';
import type { BeanState } from '@/types';

interface DungeonCellProps {
  beanState: BeanState;
  onBeanReady?: () => void;
}

export default function DungeonCell({ beanState, onBeanReady }: DungeonCellProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<import('phaser').Game | null>(null);
  const prevStateRef = useRef<BeanState>('idle');

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    let game: import('phaser').Game;

    import('phaser').then((Phaser) => {
      import('./phaser/BeanCellScene').then(({ BeanCellScene }) => {
        game = new Phaser.Game({
          type: Phaser.AUTO,
          width: 600,
          height: 400,
          backgroundColor: '#e8e0d0',
          scene: [BeanCellScene],
          parent: containerRef.current!,
          scale: {
            mode: Phaser.Scale.FIT,
            autoCenter: Phaser.Scale.CENTER_BOTH,
          },
          audio: { disableWebAudio: true },
          render: { antialias: false, pixelArt: true },
        });
        gameRef.current = game;
        onBeanReady?.();
      });
    });

    return () => {
      game?.destroy(true);
      gameRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Relay state changes to Phaser
  useEffect(() => {
    if (!gameRef.current || beanState === prevStateRef.current) return;
    prevStateRef.current = beanState;
    gameRef.current.events.emit('bean:state', beanState);
  }, [beanState]);

  return (
    <div
      ref={containerRef}
      className="w-full aspect-[3/2] bg-[#e8e0d0]"
      style={{ maxWidth: 600, maxHeight: 400 }}
    />
  );
}

// Helper to emit events from outside (used by parent components)
export function emitBeanEvent(
  gameRef: React.RefObject<import('phaser').Game | null>,
  event: string,
  data?: unknown
) {
  gameRef.current?.events.emit(event, data);
}
