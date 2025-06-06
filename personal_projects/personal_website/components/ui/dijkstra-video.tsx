'use client';

export default function DijkstraVideo() {
  return (
    <video
      autoPlay
      loop
      muted
      playsInline
      width={600}
      className="rounded-xl shadow-lg"
    >
      <source src="/assets/dijkstra.webm" type="video/webm" />
      <source src="/assets/dijkstra.mp4"  type="video/mp4" />
      Sorry—your browser can’t play this demo video.
    </video>
  );
}
