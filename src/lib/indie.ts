export const INDIE_TAGS = new Set([
  "linux",
  "debian",
  "ubuntu",
  "arch",
  "nixos",
  "fedora",
  "alpine",
  "self-hosting",
  "homelab",
  "indie",
  "cli",
  "terminal",
  "shell",
  "systemd",
  "docker",
  "podman",
  "docker-compose",
  "compose",
  "k3s",
  "proxmox",
  "lxc",
  "nginx",
  "caddy",
  "traefik",
  "reverse-proxy",
  "tailscale",
  "wireguard",
  "vpn",
  "cloudflared",
  "zerotier",
  "raspberry",
  "homeassistant",
  "adguardhome",
  "pihole",
  "git",
  "ssh",
  "borgbackup",
  "restic",
  "ansible",
  "servidor",
  "filosofia",
]);

export function isIndiePost(p: any) {
  if (!p) return false;
  if (p.data?.draft) return false;
  const slug = p.slug || "";
  if (slug === "que-significa-indie-en-linux") return true;
  const tags = (p.data?.tags || []).map((t: string) => String(t).toLowerCase().trim());
  if (tags.length === 0) return false;
  return tags.some((t: string) => INDIE_TAGS.has(t));
}

export async function getIndiePosts(getCollection: any) {
  const posts = await getCollection("posts");
  return posts.filter(isIndiePost).sort(
    (a: any, b: any) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );
}
