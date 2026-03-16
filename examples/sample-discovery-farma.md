# Discovery Notes — Laboratorios Farma SA
# Reunión: 12 marzo 2026
# Asistentes: CTO (Roberto), DBA lead (Patricia), Dev lead (Andrés)

Base Oracle 19c Enterprise en VMware on-prem
- 800GB OLTP, producción, sistema core de trazabilidad de medicamentos
- 12 vCPUs, 64GB RAM en VM
- CPU promedio 45%, picos a 75% fin de mes cuando cierran lotes
- Unos 80 usuarios concurrentes, picos de 150
- TDE habilitado, tienen BYOL con 2 proc licenses
- Backup con RMAN a disco local, no tienen copia offsite

Aplicación Java en Tomcat, 2 servidores app
- Conexión JDBC simple, no usan pool avanzado
- Quieren eventualmente pasar a containers pero no es prioridad ahora

No tienen DR. Patricia dijo "si se cae, tardamos 8hs en restaurar del backup"
Roberto quiere DR pero no quiere pagar el doble
RTO aceptable: 1 hora. RPO: 15 minutos max

Regulación ANMAT — necesitan audit trail completo, no pueden perder datos de trazabilidad
No mencionaron PCI ni HIPAA

Red: tienen un link de internet de 100Mbps, no tienen FastConnect ni VPN dedicada
Patricia preguntó si pueden seguir usando SQLDeveloper y RMAN

Presupuesto: quieren gastar menos que hoy. Hoy pagan ~$15K USD/mes entre licencias + hosting del datacenter
Timeline: "no hay apuro pero si se puede antes de fin de año mejor"
No están mirando AWS ni Azure, solo OCI porque ya tienen las licencias Oracle

Andrés preguntó por APEX — tienen una app interna de reportes que quieren modernizar
Patricia mencionó que usan algunos jobs con DBMS_SCHEDULER y tienen 3 DB links a otros sistemas