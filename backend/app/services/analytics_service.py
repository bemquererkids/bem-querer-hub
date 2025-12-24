"""
Analytics Service
Provides metrics and statistics queries for Carol AI.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.database import get_supabase_client

class AnalyticsService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_metric(
        self,
        tipo_metrica: str,
        periodo: str,
        clinica_id: str
    ) -> Dict[str, Any]:
        """
        Roteador principal para métricas.
        
        Args:
            tipo_metrica: 'leads', 'agendamentos', 'comparecimentos', 'vendas', 'conversao'
            periodo: 'hoje', 'semana', 'mes', 'mes_passado', 'ano'
            clinica_id: UUID da clínica
        """
        # Calcular datas
        date_range = self._get_date_range(periodo)
        
        # Rotear para função específica
        if tipo_metrica == "leads":
            return await self._get_leads_metric(clinica_id, date_range)
        elif tipo_metrica == "agendamentos":
            return await self._get_appointments_metric(clinica_id, date_range)
        elif tipo_metrica == "comparecimentos":
            return await self._get_attendance_metric(clinica_id, date_range)
        elif tipo_metrica == "vendas":
            return await self._get_sales_metric(clinica_id, date_range)
        elif tipo_metrica == "conversao":
            return await self._get_conversion_metric(clinica_id, date_range)
        else:
            return {"error": f"Métrica '{tipo_metrica}' não reconhecida"}
    
    def _get_date_range(self, periodo: str) -> Dict[str, datetime]:
        """Calcula range de datas baseado no período."""
        now = datetime.now()
        
        if periodo == "hoje":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif periodo == "semana":
            start = now - timedelta(days=7)
            end = now
        elif periodo == "mes":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif periodo == "mes_passado":
            # Primeiro dia do mês passado
            first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            start = last_day_last_month.replace(day=1)
            end = last_day_last_month.replace(hour=23, minute=59, second=59)
        elif periodo == "ano":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            # Default: últimos 30 dias
            start = now - timedelta(days=30)
            end = now
        
        return {"start": start, "end": end}
    
    async def _get_leads_metric(self, clinica_id: str, date_range: Dict) -> Dict[str, Any]:
        """Consulta total de leads."""
        try:
            # Query para contar leads
            response = self.supabase.table("deals").select(
                "id, status, created_at",
                count="exact"
            ).eq(
                "clinica_id", clinica_id
            ).gte(
                "created_at", date_range["start"].isoformat()
            ).lte(
                "created_at", date_range["end"].isoformat()
            ).execute()
            
            total = len(response.data) if response.data else 0
            
            # Contar quantos viraram agendamento
            agendados = sum(1 for deal in response.data if deal.get("status") in ["scheduled", "attended", "noshow"])
            
            return {
                "total_leads": total,
                "leads_agendados": agendados,
                "taxa_conversao": round((agendados / total * 100), 1) if total > 0 else 0,
                "periodo": f"{date_range['start'].strftime('%d/%m')} a {date_range['end'].strftime('%d/%m')}"
            }
        except Exception as e:
            print(f"[Analytics Error] get_leads_metric: {e}")
            return {"error": str(e)}
    
    async def _get_appointments_metric(self, clinica_id: str, date_range: Dict) -> Dict[str, Any]:
        """Consulta agendamentos."""
        try:
            response = self.supabase.table("deals").select(
                "id, status, updated_at"
            ).eq(
                "clinica_id", clinica_id
            ).in_(
                "status", ["scheduled", "attended", "noshow"]
            ).gte(
                "updated_at", date_range["start"].isoformat()
            ).lte(
                "updated_at", date_range["end"].isoformat()
            ).execute()
            
            total = len(response.data) if response.data else 0
            
            return {
                "total_agendamentos": total,
                "periodo": f"{date_range['start'].strftime('%d/%m')} a {date_range['end'].strftime('%d/%m')}"
            }
        except Exception as e:
            print(f"[Analytics Error] get_appointments_metric: {e}")
            return {"error": str(e)}
    
    async def _get_attendance_metric(self, clinica_id: str, date_range: Dict) -> Dict[str, Any]:
        """Consulta taxa de comparecimento."""
        try:
            response = self.supabase.table("deals").select(
                "id, status"
            ).eq(
                "clinica_id", clinica_id
            ).in_(
                "status", ["attended", "noshow"]
            ).gte(
                "updated_at", date_range["start"].isoformat()
            ).lte(
                "updated_at", date_range["end"].isoformat()
            ).execute()
            
            total = len(response.data) if response.data else 0
            compareceram = sum(1 for deal in response.data if deal.get("status") == "attended")
            
            taxa = round((compareceram / total * 100), 1) if total > 0 else 0
            
            return {
                "total_agendados": total,
                "compareceram": compareceram,
                "faltaram": total - compareceram,
                "taxa_comparecimento": taxa,
                "periodo": f"{date_range['start'].strftime('%d/%m')} a {date_range['end'].strftime('%d/%m')}"
            }
        except Exception as e:
            print(f"[Analytics Error] get_attendance_metric: {e}")
            return {"error": str(e)}
    
    async def _get_sales_metric(self, clinica_id: str, date_range: Dict) -> Dict[str, Any]:
        """Consulta vendas realizadas."""
        try:
            # Assumindo que vendas são deals com status 'won' ou similar
            response = self.supabase.table("deals").select(
                "id, value, procedure"
            ).eq(
                "clinica_id", clinica_id
            ).eq(
                "status", "won"
            ).gte(
                "updated_at", date_range["start"].isoformat()
            ).lte(
                "updated_at", date_range["end"].isoformat()
            ).execute()
            
            total_vendas = len(response.data) if response.data else 0
            
            # Calcular faturamento (se houver campo value)
            faturamento = sum(deal.get("value", 0) for deal in response.data)
            ticket_medio = round(faturamento / total_vendas, 2) if total_vendas > 0 else 0
            
            return {
                "total_vendas": total_vendas,
                "faturamento": faturamento,
                "ticket_medio": ticket_medio,
                "periodo": f"{date_range['start'].strftime('%d/%m')} a {date_range['end'].strftime('%d/%m')}"
            }
        except Exception as e:
            print(f"[Analytics Error] get_sales_metric: {e}")
            return {"error": str(e)}
    
    async def _get_conversion_metric(self, clinica_id: str, date_range: Dict) -> Dict[str, Any]:
        """Calcula taxa de conversão geral."""
        leads_data = await self._get_leads_metric(clinica_id, date_range)
        sales_data = await self._get_sales_metric(clinica_id, date_range)
        
        total_leads = leads_data.get("total_leads", 0)
        total_vendas = sales_data.get("total_vendas", 0)
        
        taxa = round((total_vendas / total_leads * 100), 1) if total_leads > 0 else 0
        
        return {
            "total_leads": total_leads,
            "total_vendas": total_vendas,
            "taxa_conversao_vendas": taxa,
            "periodo": leads_data.get("periodo", "")
        }

# Singleton
analytics_service = AnalyticsService()
