{{- define "agentspring.name" -}}
agentspring
{{- end -}}

{{- define "agentspring.fullname" -}}
{{ include "agentspring.name" . }}
{{- end -}}
