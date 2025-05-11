import { NoopConfig } from 'motia'

export const config: NoopConfig = {
  type: 'noop',
  name: 'Flow Starter',
  description: 'Start the default flow',
  virtualSubscribes: [],
  virtualEmits: ['/default'],
  flows: ['default'],
} 