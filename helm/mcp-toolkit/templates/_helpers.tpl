{{/*
Return the service account name to use.
*/}}
{{- define "mcp-toolkit.serviceAccountName" -}}
{{- if .Values.serviceAccount.name -}}
{{ .Values.serviceAccount.name }}
{{- else -}}
{{ .Release.Name }}
{{- end -}}
{{- end -}}
