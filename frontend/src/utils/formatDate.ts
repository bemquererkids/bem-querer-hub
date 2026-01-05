
export function formatTime(timestamp: string | null): string {
    if (!timestamp) return '';

    try {
        const date = new Date(timestamp);
        // Check for invalid date
        if (isNaN(date.getTime())) return '';

        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const oneDay = 86400000;

        // Check if it's today
        const isToday = date.getDate() === now.getDate() &&
            date.getMonth() === now.getMonth() &&
            date.getFullYear() === now.getFullYear();

        if (isToday) {
            return date.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        // Check if it's yesterday
        const yesterday = new Date(now);
        yesterday.setDate(now.getDate() - 1);
        const isYesterday = date.getDate() === yesterday.getDate() &&
            date.getMonth() === yesterday.getMonth() &&
            date.getFullYear() === yesterday.getFullYear();

        if (isYesterday) {
            return 'Ontem';
        }

        // Less than 7 days - show weekday
        if (diff < 7 * oneDay) {
            return date.toLocaleDateString('pt-BR', { weekday: 'short' }).replace('.', '');
        }

        // Older - show date
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (e) {
        return '';
    }
}
