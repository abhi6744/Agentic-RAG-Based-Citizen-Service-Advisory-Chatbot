export function cleanText(value: string | undefined | null): string {
    if (!value) return "";
    let clean = value;
    
    // Replace breaks with newlines
    clean = clean.replace(/<br\s*\/?>/gi, '\n');
    clean = clean.replace(/<\/li>\s*<li>/gi, '\n');
    clean = clean.replace(/<li[^>]*>/gi, '');
    clean = clean.replace(/<\/li>/gi, '');
    
    // Remove other html tags
    clean = clean.replace(/<\/?(ul|ol|p|strong|b|em|i|div|span)[^>]*>/gi, '');
    clean = clean.replace(/<[^>]+>/g, '');
    
    // Unescape common HTML entities
    clean = clean.replace(/&amp;/g, '&');
    clean = clean.replace(/&lt;/g, '<');
    clean = clean.replace(/&gt;/g, '>');
    clean = clean.replace(/&quot;/g, '"');
    clean = clean.replace(/&#39;/g, "'");
    
    // Cleanup spacing
    clean = clean.replace(/[ \t]+/g, ' ');
    clean = clean.replace(/\n[ \t]+/g, '\n');
    
    // Remove rogue markdown bold/italics
    clean = clean.replace(/\*\*/g, '');
    clean = clean.replace(/__/g, '');
    
    return clean.trim();
}
