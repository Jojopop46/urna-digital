import { defineStore } from 'pinia'

interface ZKCommitment {
  commitment_x: string
  commitment_y: string
  nullifier: string
  receipt_token: string
}

export const useVotingStore = defineStore('voting', {
  state: () => ({
    commitment: null as ZKCommitment | null,
    step: 'identity' as 'identity' | 'selection' | 'confirmation' | 'receipt'
  }),
  actions: {
    async submitVote(processId: string, voteIndex: number, numOptions: number, identityHash: string) {
      const res = await fetch('/api/v1/vote/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ process_id: processId, vote_index: voteIndex, num_options: numOptions, identity_hash: identityHash })
      })
      if (!res.ok) throw new Error(await res.text())
      this.commitment = await res.json()
      this.step = 'receipt'
    }
  }
})
