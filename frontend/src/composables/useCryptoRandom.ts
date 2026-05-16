export function useCryptoRandom() {
  function randomHex(length: number): string {
    const arr = new Uint8Array(Math.ceil(length / 2))
    window.crypto.getRandomValues(arr)
    return Array.from(arr, (b) => b.toString(16).padStart(2, '0')).join('').slice(0, length)
  }

  function randomId(prefix: string): string {
    return `${prefix}_${randomHex(16)}`
  }

  return { randomHex, randomId }
}
