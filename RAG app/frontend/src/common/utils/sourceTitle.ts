import type { Source } from '../types/api';

// Use saved titles or a readable URL path, without generation, network calls or database writes.
export function sourceDisplayTitle(
  source: Pick<Source, 'title' | 'url'>,
  capturedTitle?: string,
): string {
  let url: URL;
  try {
    url = new URL(source.url);
  } catch {
    return source.title?.trim() || 'Official source';
  }
  const generic = /^(home|index|default|untitled|document|official source|page)$/i;
  for (const title of [source.title, capturedTitle]) {
    const value = title?.replace(/\s+/g, ' ').trim();
    if (
      value &&
      !/^https?:\/\//i.test(value) &&
      !generic.test(value) &&
      value.replace(/^www\./i, '').replace(/\/$/, '') !== url.hostname.replace(/^www\./i, '')
    )
      return value;
  }
  const ignored =
    /^(en|ar|en-us|en-ae|pages?|index|default|home|web|wps|portal|services?|servicecatalog)$/i;
  for (const part of url.pathname.split('/').reverse()) {
    let label: string;
    try {
      label = decodeURIComponent(part).replace(/\.(html?|aspx?|php|pdf)$/i, '');
    } catch {
      continue;
    }
    if (!label || ignored.test(label) || /^\d+$/.test(label) || /^[a-f0-9-]{24,}$/i.test(label))
      continue;
    label = label.replace(/[-_]+/g, ' ').replace(/\s+/g, ' ').trim();
    if (label)
      return (label.charAt(0).toUpperCase() + label.slice(1)).replace(
        /\b(uae|it|llc|faq)\b/gi,
        (word) => word.toUpperCase(),
      );
  }
  return url.hostname.replace(/^www\./i, '');
}
