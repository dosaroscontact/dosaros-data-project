import { Composition } from 'remotion'
import { LaunchVideo } from './LaunchVideo'

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="LaunchVideo"
        component={LaunchVideo}
        durationInFrames={750}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ format: 'vertical' as const }}
      />
      <Composition
        id="LaunchSquare"
        component={LaunchVideo}
        durationInFrames={750}
        fps={30}
        width={1080}
        height={1080}
        defaultProps={{ format: 'square' as const }}
      />
      <Composition
        id="LaunchHorizontal"
        component={LaunchVideo}
        durationInFrames={750}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ format: 'horizontal' as const }}
      />
    </>
  )
}
