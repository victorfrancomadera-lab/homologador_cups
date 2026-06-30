import { useEffect, useRef, useState } from 'react'
import api from '../api'
import { useAuth } from '../auth'

const pesos = (n) =>
  n == null ? '—' : '$' + Number(n).toLocaleString('es-CO')

export default function Buscador() {
  const { user } = useAuth()
  const [q, setQ] = useState('')
  const [sug, setSug] = useState([])
  const [showSug, setShowSug] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const debRef = useRef(null)
  const boxRef = useRef(null)

  // Autocompletado con debounce
  useEffect(() => {
    if (q.trim().length < 2) {
      setSug([])
      return
    }
    clearTimeout(debRef.current)
    debRef.current = setTimeout(async () => {
      try {
        const { data } = await api.get('/api/search/sugerencias', { params: { q: q.trim() } })
        setSug(data)
        setShowSug(true)
      } catch {
        setSug([])
      }
    }, 250)
    return () => clearTimeout(debRef.current)
  }, [q])

  useEffect(() => {
    const onClick = (e) => {
      if (boxRef.current && !boxRef.current.contains(e.target)) setShowSug(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  async function buscar(codigo) {
    const code = (codigo || q).trim()
    if (!code) return
    setShowSug(false)
    setBusy(true)
    setError('')
    setResult(null)
    try {
      const { data } = await api.get(`/api/search/${encodeURIComponent(code)}`)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al consultar')
    } finally {
      setBusy(false)
    }
  }

  function elegir(s) {
    setQ(s.codigo)
    setShowSug(false)
    buscar(s.codigo)
  }

  return (
    <div className="container">
      <h2 style={{ color: '#093a66', marginBottom: 4 }}>Consulta de código CUPS</h2>
      <p className="muted" style={{ marginTop: 0, marginBottom: 18 }}>
        Verifica la vigencia y consulta las equivalencias en el Manual Tarifario SOAT (2025)
        y el Manual ISS 2001 (Acuerdo 256/2001).
      </p>

      <div className="search-box" ref={boxRef}>
        <input
          placeholder="Escribe un código CUPS o parte del nombre…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && buscar()}
          onFocus={() => sug.length && setShowSug(true)}
        />
        {showSug && sug.length > 0 && (
          <div className="suggestions">
            {sug.map((s) => (
              <div key={s.codigo} onClick={() => elegir(s)}>
                <span className="cod">{s.codigo}</span>
                {s.nombre}
                {!s.vigente && <span className="no-vig">NO VIGENTE</span>}
              </div>
            ))}
          </div>
        )}
      </div>
      <button className="btn btn-sm" style={{ marginTop: 12 }} onClick={() => buscar()} disabled={busy}>
        {busy ? 'Buscando…' : 'Consultar'}
      </button>

      {error && <div className="error" style={{ marginTop: 18 }}>{error}</div>}

      {result && <Resultado data={result} user={user} onBuscar={(c) => { setQ(c); buscar(c) }} />}
    </div>
  )
}

function Resultado({ data, user, onBuscar }) {
  const estadoTxt = {
    VIGENTE: 'VIGENTE',
    NO_VIGENTE: 'NO VIGENTE',
    NO_ENCONTRADO: 'NO ENCONTRADO',
  }[data.estado]

  return (
    <div className="card">
      <span className={`estado ${data.estado}`}>{estadoTxt}</span>
      <div className="codigo-titulo">
        {data.cups ? `${data.cups.codigo} · ${data.cups.nombre}` : data.consulta}
      </div>
      {data.cups?.capitulo && <div className="cap">{data.cups.capitulo}</div>}
      {data.mensaje && <div className="mensaje">{data.mensaje}</div>}

      {data.reemplazo && (
        <div className="mensaje">
          Código de reemplazo:{' '}
          <a onClick={() => onBuscar(data.reemplazo.codigo)} style={{ cursor: 'pointer', fontWeight: 700 }}>
            {data.reemplazo.codigo}
          </a>{' '}— {data.reemplazo.nombre}
        </div>
      )}

      {data.estado === 'VIGENTE' && (
        <>
          {/* SOAT */}
          {user.can_view_soat && (
            <>
              <div className="seccion-titulo">
                Equivalencia SOAT <span className="badge-fuente">Manual SOAT 2025</span>
              </div>
              {data.soat.length === 0 ? (
                <div className="vacio">Sin equivalencia registrada en el Manual SOAT.</div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Código</th><th>Descripción</th><th>Clase</th><th>Cobertura</th>
                      <th>UVB</th><th>Valor a cobrar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.soat.map((s, i) => (
                      <tr key={i}>
                        <td>{s.codigo_soat || '—'}</td>
                        <td>{s.descripcion_soat}</td>
                        <td>{s.clase}</td>
                        <td>{s.cobertura}</td>
                        <td>{s.uvb || '—'}</td>
                        <td className="valor">{pesos(s.valor_pesos)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </>
          )}

          {/* ISS 2001 */}
          {user.can_view_iss && (
            <>
              <div className="seccion-titulo">
                Equivalencia ISS 2001 <span className="badge-fuente">Acuerdo 256/2001</span>
              </div>
              {data.iss.length === 0 ? (
                <div className="vacio">Sin equivalencia registrada en el Manual ISS 2001.</div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Código ISS</th><th>Descripción</th><th>Tipo</th>
                      <th>UVR</th><th>Valor a cobrar (pesos 2001)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.iss.map((it, i) => (
                      <tr key={i}>
                        <td>{it.codigo_iss || '—'}</td>
                        <td>{it.descripcion}</td>
                        <td>{it.tipo_valor === 'UVR' ? 'Quirúrgico (UVR)' : 'Tarifa directa'}</td>
                        <td>{it.uvr != null ? <span className="uvr-pill">{it.uvr}</span> : '—'}</td>
                        <td>
                          {it.tipo_valor === 'UVR' ? (
                            <ul className="roles">
                              {it.valores_por_rol.map((v, j) => (
                                <li key={j}>
                                  <span>{v.rol}</span>
                                  <span>{pesos(v.valor_pesos)}</span>
                                </li>
                              ))}
                            </ul>
                          ) : it.valor_pesos != null ? (
                            <span className="valor">{pesos(it.valor_pesos)}</span>
                          ) : (
                            <span className="muted">Valor por verificar</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </>
          )}

          {!user.can_view_soat && !user.can_view_iss && (
            <div className="sin-permiso" style={{ marginTop: 20 }}>
              Tu cuenta no tiene habilitada la visualización de equivalencias tarifarias.
              Contacta al administrador.
            </div>
          )}
        </>
      )}
    </div>
  )
}
