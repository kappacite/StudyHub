import os
from flask import Flask, request
from flask_cors import CORS
from app.config import config_by_name
from app.extensions import db, jwt, migrate, limiter, redis_client, celery_app

def create_app(config_name=None):
    flask_app = Flask(__name__)
    
    # Whitelist CORS stricte ciblant l'URL du frontend
    allowed_origins = os.environ.get(
        "CORS_ALLOWED_ORIGINS", 
        "https://study.leshen.cloud,http://localhost:5173,http://localhost:3000"
    )
    origins_list = [o.strip() for o in allowed_origins.split(",") if o.strip()]
    
    CORS(flask_app, resources={r"/api/.*": {
        "origins": origins_list,
        "allow_headers": ["Content-Type", "Authorization", "Signature-Agent", "Signature", "Signature-Input", "X-Requested-With", "Accept", "Origin"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    }})
    
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "development")
        
    flask_app.config.from_object(config_by_name[config_name])
    
    # Faire confiance aux en-têtes du proxy inverse (Nginx / Cloudflare)
    from werkzeug.middleware.proxy_fix import ProxyFix
    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialisation des extensions
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    redis_client.init_app(flask_app)
    migrate.init_app(flask_app, db)
    limiter.init_app(flask_app)
    
    # Configuration de Celery
    celery_app.config_from_object(flask_app.config, namespace="CELERY")

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            from flask import has_app_context
            # En exécution eager (tests) ou inline pendant une requête, un contexte
            # applicatif est déjà actif : on le réutilise pour rester sur la bonne
            # base. Sinon (worker Celery réel), on pousse le contexte de l'app.
            if has_app_context():
                return self.run(*args, **kwargs)
            with flask_app.app_context():
                return self.run(*args, **kwargs)
    celery_app.Task = ContextTask

    
    # Configuration de Talisman pour les en-têtes de sécurité
    from flask_talisman import Talisman
    csp = {
        'default-src': '\'self\'',
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '\'unsafe-eval\'',
            'https://static.cloudflareinsights.com'
        ],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'https://fonts.googleapis.com'
        ],
        'font-src': [
            '\'self\'',
            'https://fonts.gstatic.com',
            'data:'
        ],
        'img-src': [
            '\'self\'',
            'data:',
            'blob:'
        ],
        'connect-src': [
            '\'self\'',
            'https://static.cloudflareinsights.com'
        ],
        'worker-src': [
            '\'self\'',
            'blob:'
        ],
        'frame-src': '\'self\''
    }
    Talisman(flask_app,
             content_security_policy=csp,
             force_https=(config_name == "production"),
             strict_transport_security=True,
             strict_transport_security_max_age=31536000,
             strict_transport_security_include_subdomains=True,
             strict_transport_security_preload=True,
             frame_options="SAMEORIGIN",
             referrer_policy="strict-origin-when-cross-origin")
    
    # Assurer que le dossier d'upload existe
    os.makedirs(flask_app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Enregistrement des middlewares et des routes (à faire après leur création)
    with flask_app.app_context():
        # Forcer l'enregistrement des callbacks JWT
        import app.middlewares.auth_middleware
        
        # Enregistrement des gestionnaires d'erreurs globaux
        from app.middlewares.error_handler import register_error_handlers
        register_error_handlers(flask_app)
        
        # Enregistrement du logger de requêtes
        from app.middlewares.request_logger import register_request_logger
        register_request_logger(flask_app)
        
        # Enregistrement des blueprints
        from app.api.v1.auth import auth_bp
        from app.api.v1.users import users_bp
        from app.api.v1.binders import binders_bp
        from app.api.v1.decks import decks_bp
        from app.api.v1.flashcards import flashcards_bp, flashcards_global_bp
        from app.api.v1.notes import notes_bp
        from app.api.v1.diagrams import diagrams_bp
        from app.api.v1.pdfs import pdfs_bp
        from app.api.v1.stats import stats_bp
        from app.api.v1.health import health_bp
        from app.api.v1.blurting import blurting_bp
        from app.api.v1.packages import packages_bp
        from app.api.v1.tags import tags_bp
        from app.api.v1.focus import focus_bp
        from app.api.v1.planning import planning_bp
        from app.api.v1.search import search_bp
        from app.api.v1.imports import imports_bp
        from app.api.v1.quizzes import quizzes_bp
        from app.api.v1.evaluations import evaluations_bp
        from app.api.v1.exam import exam_bp
        from app.api.v1.groups import groups_bp
        from app.api.v1.classes import classes_bp, assignments_mine_bp
        
        flask_app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
        flask_app.register_blueprint(users_bp, url_prefix="/api/v1/users")
        flask_app.register_blueprint(binders_bp, url_prefix="/api/v1/binders")
        flask_app.register_blueprint(decks_bp, url_prefix="/api/v1/decks")
        flask_app.register_blueprint(flashcards_bp, url_prefix="/api/v1/decks/<int:deck_id>/cards")
        flask_app.register_blueprint(flashcards_global_bp, url_prefix="/api/v1/flashcards")
        flask_app.register_blueprint(notes_bp, url_prefix="/api/v1/notes")
        flask_app.register_blueprint(diagrams_bp, url_prefix="/api/v1/diagrams")
        flask_app.register_blueprint(pdfs_bp, url_prefix="/api/v1/pdfs")
        flask_app.register_blueprint(stats_bp, url_prefix="/api/v1/stats")
        flask_app.register_blueprint(health_bp, url_prefix="/api/v1/health")
        flask_app.register_blueprint(blurting_bp, url_prefix="/api/v1/blurting")
        flask_app.register_blueprint(packages_bp, url_prefix="/api/v1/packages")
        flask_app.register_blueprint(tags_bp, url_prefix="/api/v1/tags")
        flask_app.register_blueprint(focus_bp, url_prefix="/api/v1/focus")
        flask_app.register_blueprint(planning_bp, url_prefix="/api/v1/planning")
        flask_app.register_blueprint(search_bp, url_prefix="/api/v1/search")
        flask_app.register_blueprint(imports_bp, url_prefix="/api/v1/import")
        flask_app.register_blueprint(quizzes_bp, url_prefix="/api/v1/quizzes")
        flask_app.register_blueprint(evaluations_bp, url_prefix="/api/v1/evaluations")
        flask_app.register_blueprint(exam_bp, url_prefix="/api/v1/exam")
        flask_app.register_blueprint(groups_bp, url_prefix="/api/v1/groups")
        flask_app.register_blueprint(classes_bp, url_prefix="/api/v1/classes")
        flask_app.register_blueprint(assignments_mine_bp, url_prefix="/api/v1/assignments")
        
        # Import all models so Alembic can detect them and db.create_all() works
        import app.models.user
        import app.models.binder
        import app.models.deck
        import app.models.flashcard
        import app.models.note
        import app.models.diagram
        import app.models.pdf_document
        import app.models.study_session
        import app.models.tag
        import app.models.quiz
        import app.models.exam
        import app.models.group
        import app.models.assignment
        import app.models.hidden_note
        
        # Import celery tasks
        import app.tasks


        # La factory reste pure : pas de migration ici (pour ne pas interférer avec
        # les commandes `flask db ...`). L'auto-migration au démarrage est gérée par
        # l'entrypoint serveur wsgi.py (run_auto_migrations). Les tests gèrent leur
        # schéma via db.create_all().
        pass
            
        @flask_app.route("/sitemap.xml", methods=["GET"])
        def sitemap():
            from app.models.note import Note
            from app.models.binder import Binder
            from flask import make_response
            
            base_url = "https://study.leshen.cloud"
            
            # 1. Pages statiques
            pages = [
                {"loc": f"{base_url}/", "changefreq": "daily", "priority": "1.0"},
                {"loc": f"{base_url}/explore", "changefreq": "daily", "priority": "0.8"},
                {"loc": f"{base_url}/login", "changefreq": "weekly", "priority": "0.5"},
                {"loc": f"{base_url}/register", "changefreq": "weekly", "priority": "0.5"},
            ]
            
            # 2. Binders (packages) publics
            try:
                public_binders = Binder.query.filter_by(is_public=True).all()
                for binder in public_binders:
                    pages.append({
                        "loc": f"{base_url}/package/{binder.id}",
                        "changefreq": "weekly",
                        "priority": "0.7",
                        "lastmod": binder.updated_at.strftime("%Y-%m-%d") if binder.updated_at else None
                    })
            except Exception as e:
                flask_app.logger.error(f"Erreur sitemap binders: {e}")
                
            # 3. Notes publiques
            try:
                public_notes = Note.query.filter_by(is_public=True).filter(Note.share_token.isnot(None)).all()
                for note in public_notes:
                    pages.append({
                        "loc": f"{base_url}/notes/public/{note.share_token}",
                        "changefreq": "weekly",
                        "priority": "0.6",
                        "lastmod": note.updated_at.strftime("%Y-%m-%d") if note.updated_at else None
                    })
            except Exception as e:
                flask_app.logger.error(f"Erreur sitemap notes: {e}")
                
            # Génération XML
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            for page in pages:
                xml_content += '  <url>\n'
                xml_content += f'    <loc>{page["loc"]}</loc>\n'
                if "lastmod" in page and page["lastmod"]:
                    xml_content += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
                xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
                xml_content += f'    <priority>{page["priority"]}</priority>\n'
                xml_content += '  </url>\n'
            xml_content += '</urlset>\n'
            
            response = make_response(xml_content)
            response.headers["Content-Type"] = "application/xml"
            return response

        @flask_app.route("/.well-known/api-catalog", methods=["GET"])
        def api_catalog():
            from flask import jsonify
            catalog = {
                "linkset": [
                    {
                        "anchor": "https://study.leshen.cloud/api/v1",
                        "service-desc": [
                            {"href": "https://study.leshen.cloud/docs/openapi.json", "type": "application/openapi+json"}
                        ],
                        "service-doc": [
                            {"href": "https://study.leshen.cloud/docs/api", "type": "text/html"}
                        ],
                        "status": [
                            {"href": "https://study.leshen.cloud/api/v1/health", "type": "application/json"}
                        ]
                    }
                ]
            }
            response = jsonify(catalog)
            response.headers["Content-Type"] = "application/linkset+json; charset=utf-8"
            return response

        @flask_app.route("/.well-known/openid-configuration", methods=["GET"])
        @flask_app.route("/.well-known/oauth-authorization-server", methods=["GET"])
        def oauth_discovery():
            from flask import jsonify
            discovery = {
                "issuer": "https://study.leshen.cloud",
                "authorization_endpoint": "https://study.leshen.cloud/login",
                "token_endpoint": "https://study.leshen.cloud/api/v1/auth/login",
                "jwks_uri": "https://study.leshen.cloud/api/v1/auth/jwks",
                "grant_types_supported": ["password", "refresh_token"],
                "response_types_supported": ["token"],
                "agent_auth": {
                    "skill": "https://isitagentready.com/.well-known/agent-skills/auth-md/SKILL.md",
                    "register_uri": "https://study.leshen.cloud/register",
                    "identity_types_supported": ["anonymous", "email"],
                    "anonymous": {
                        "credential_types_supported": ["api_key"]
                    },
                    "identity_assertion": {
                        "assertion_types_supported": ["verified_email"]
                    }
                }
            }
            return jsonify(discovery)

        @flask_app.route("/.well-known/oauth-protected-resource", methods=["GET"])
        def oauth_protected_resource():
            from flask import jsonify
            prm = {
                "resource": "https://study.leshen.cloud/api/v1",
                "authorization_servers": ["https://study.leshen.cloud"],
                "scopes_supported": ["read", "write"],
                "bearer_methods_supported": ["header"]
            }
            return jsonify(prm)

        @flask_app.route("/.well-known/agent-card.json", methods=["GET"])
        def agent_card():
            from flask import jsonify
            card = {
                "name": "StudyHub Assistant",
                "version": "1.0.0",
                "description": "Assistant d'étude IA pour la révision par flashcards, notes et blurting.",
                "supportedInterfaces": [
                    {
                        "url": "https://study.leshen.cloud/api/v1/a2a",
                        "protocol": "http"
                    }
                ],
                "capabilities": ["text-processing", "repetition-spaced-SM2", "blurting-analysis"],
                "skills": [
                    {
                        "id": "study-sm2",
                        "name": "SuperMemo-2",
                        "description": "Algorithme de révision espacée pour mémorisation active."
                    },
                    {
                        "id": "blurting-ai",
                        "name": "Blurting Analysis",
                        "description": "Analyse de restitution de mémoire par IA."
                    }
                ]
            }
            return jsonify(card)

        @flask_app.route("/.well-known/agent-skills/index.json", methods=["GET"])
        def agent_skills_index():
            from flask import jsonify
            import hashlib
            
            skill_content = "# study-sm2\nAlgorithme de révision espacée pour mémorisation active.\n"
            h = hashlib.sha256(skill_content.encode("utf-8")).hexdigest()
            
            index_data = {
                "$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
                "skills": [
                    {
                        "name": "study-sm2",
                        "type": "skill-md",
                        "description": "Algorithme de révision espacée pour mémorisation active.",
                        "url": "https://study.leshen.cloud/.well-known/agent-skills/study-sm2/SKILL.md",
                        "digest": f"sha256:{h}"
                    }
                ]
            }
            return jsonify(index_data)

        @flask_app.route("/.well-known/agent-skills/study-sm2/SKILL.md", methods=["GET"])
        def agent_skill_md():
            from flask import make_response
            content = "# study-sm2\nAlgorithme de révision espacée pour mémorisation active.\n"
            response = make_response(content)
            response.headers["Content-Type"] = "text/markdown; charset=utf-8"
            return response

        @flask_app.route("/.well-known/mcp/server-card.json", methods=["GET"])
        def mcp_server_card():
            from flask import jsonify
            card = {
                "serverInfo": {
                    "name": "StudyHub MCP Server",
                    "version": "1.0.0"
                },
                "endpoint": "https://study.leshen.cloud/api/v1/mcp",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                }
            }
            return jsonify(card)

        @flask_app.route("/api/v1/markdown-root", methods=["GET"])
        def markdown_root():
            from flask import make_response
            content = (
                "# StudyHub — Plateforme d'étude tout-en-un\n\n"
                "StudyHub centralise tous les outils d'apprentissage des étudiants :\n"
                "- **Flashcards & Répétition Espacée** (SuperMemo-2)\n"
                "- **Notes Scientifiques** (Markdown, LaTeX, KaTeX)\n"
                "- **Révision Blurting IA** (analyse par Gemini de vos restitutions de cours)\n"
                "- **Diagrammes Interactifs** (drag-and-drop SVG & Mermaid)\n"
                "- **Liseuse PDF & Annotations**\n"
                "- **Espace Communautaire** (Marketplace de packages de révision)\n\n"
                "Découvrez nos APIs en consultant notre catalogue d'APIs à `/.well-known/api-catalog`."
            )
            response = make_response(content)
            response.headers["Content-Type"] = "text/markdown; charset=utf-8"
            response.headers["x-markdown-tokens"] = str(len(content) // 4)
            return response

        @flask_app.after_request
        def add_security_headers(response):
            # En-têtes additionnels non gérés par Talisman
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
            response.headers["Permissions-Policy"] = "camera=(self), microphone=(), geolocation=(), interest-cohort=()"
            response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
            
            # Application de Clear-Site-Data uniquement sur la déconnexion et la suppression de compte
            if request.path in ["/api/v1/auth/logout", "/api/v1/auth/account"]:
                response.headers["Clear-Site-Data"] = '"cookies", "storage"'
                
            return response
            
    return flask_app
