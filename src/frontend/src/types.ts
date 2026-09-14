export type Band='LOW'|'MEDIUM'|'HIGH'|'CRITICAL';
export interface SiteRisk{site_id:string;site_name:string;country:string;score:number;band:Band;deviation_count:number;major_count:number;trend:number;days_since_monitoring:number;monthly_trend:{month:string;count:number}[]}
export interface Deviation{id:string;visit_id:string;patient_id:string;site_id:string;kind:string;severity:'MAJOR'|'MINOR'|'ADMINISTRATIVE';description:string;rationale:string;protocol_clause:string;confidence:number;detected_at:string;source:string}
