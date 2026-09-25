// Explain and Discuss conversations, kept per block for as long as the window is open, so
// stepping to the next block and back does not throw a discussion away.

import type { Conversation } from '../../lib/claude.svelte';

export const talks = new Map<string, Conversation>();
export const explained = new Map<string, Conversation>();
