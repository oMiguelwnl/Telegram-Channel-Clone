import configparser
import os
import asyncio
import json
from datetime import datetime
from pyrogram import Client
from pyrogram.errors import FloodWait

# Configurações iniciais
CONFIG_FILE = 'config.ini'
SESSION_FILE_FMT = 'user'

def config_exists():
    config = configparser.ConfigParser()
    return config.read(CONFIG_FILE)

def get_api_credentials():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['Credentials']['api_id'], config['Credentials']['api_hash']

def save_api_credentials(api_id, api_hash):
    config = configparser.ConfigParser()
    config['Credentials'] = {'api_id': api_id, 'api_hash': api_hash}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def save_progress(clone_name, source_id, dest_id, last_message_id, total_messages, processed_messages):
    """Salva o progresso da clonagem em JSON"""
    progress_data = {
        'clone_name': clone_name,
        'source_channel': source_id,
        'destination_channel': dest_id,
        'last_message_id': last_message_id,
        'total_messages': total_messages,
        'processed_messages': processed_messages,
        'last_update': datetime.now().isoformat(),
        'status': 'in_progress'
    }
    
    file_name = f"{clone_name}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Progresso salvo: {file_name}")

def load_progress(clone_name):
    """Carrega o progresso salvo"""
    file_name = f"{clone_name}.json"
    if not os.path.exists(file_name):
        return None
    
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def list_saved_clones():
    """Lista todas as clonagens salvas"""
    clones = []
    for file in os.listdir('.'):
        if file.endswith('.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    clones.append({
                        'file': file,
                        'name': data.get('clone_name', file.replace('.json', '')),
                        'source': data.get('source_channel', 'N/A'),
                        'dest': data.get('destination_channel', 'N/A'),
                        'last_msg': data.get('last_message_id', 0),
                        'processed': data.get('processed_messages', 0),
                        'total': data.get('total_messages', 0),
                        'status': data.get('status', 'unknown'),
                        'last_update': data.get('last_update', '')
                    })
            except:
                continue
    
    return clones

def mark_clone_completed(clone_name):
    """Marca uma clonagem como concluída"""
    file_name = f"{clone_name}.json"
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['status'] = 'completed'
            data['completed_at'] = datetime.now().isoformat()
            
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except:
            pass

async def debug_chats(app):
    """Verifica todos os chats disponíveis"""
    print("\n📡 Buscando chats...")
    
    chats = []
    try:
        async for dialog in app.get_dialogs():
            chat = dialog.chat
            if chat.type in ["channel", "group", "supergroup"]:
                chats.append({
                    'id': chat.id,
                    'title': getattr(chat, 'title', 'Sem título'),
                    'type': chat.type,
                    'username': f"@{chat.username}" if chat.username else "Sem username"
                })
        
        print(f"✅ {len(chats)} chats encontrados")
        return chats
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

async def manual_mode(app):
    """Modo manual para configurar clonagem"""
    print("\n🔧 CONFIGURAÇÃO MANUAL")
    
    # Nome da clonagem
    clone_name = input("\n📝 Nome para esta clonagem: ").strip()
    if not clone_name:
        print("❌ Nome inválido!")
        return
    
    # Verifica se já existe
    existing = load_progress(clone_name)
    if existing:
        print(f"⚠️  Já existe uma clonagem com este nome!")
        print(f"   📊 Progresso: {existing.get('processed_messages', 0)}/{existing.get('total_messages', 0)} mensagens")
        choice = input("   🔄 Continuar desta? (s/n): ").lower()
        if choice == 's':
            await continue_clone(app, clone_name, existing)
            return
    
    # Canal origem
    print("\n📥 CONFIGURAR CANAL ORIGEM:")
    source_id = await get_chat_id(app, "origem")
    if not source_id:
        return
    
    # Canal destino
    print("\n📤 CONFIGURAR CANAL DESTINO:")
    dest_id = await get_chat_id(app, "destino")
    if not dest_id:
        return
    
    # Tipo de clonagem
    mention_type = await get_mention_type()
    if not mention_type:
        return
    
    # Iniciar clonagem
    await start_clone(app, clone_name, source_id, dest_id, mention_type)

async def get_chat_id(app, purpose):
    """Obtém ID do chat com verificações"""
    while True:
        chat_input = input(f"   🔗 ID ou @username do canal {purpose}: ").strip()
        if not chat_input:
            print("   ❌ Campo obrigatório!")
            continue
        
        try:
            # Converte input
            if chat_input.startswith('@'):
                chat_id = chat_input
            else:
                chat_id = int(chat_input)
            
            # Testa acesso
            try:
                chat = await app.get_chat(chat_id)
                print(f"   ✅ {purpose.capitalize()}: {chat.title}")
                
                # Para destino, testa permissões
                if purpose == "destino":
                    try:
                        test_msg = await app.send_message(chat_id, "🧪 Teste de permissão...")
                        await test_msg.delete()
                        print("   ✅ Pode enviar mensagens!")
                    except Exception as e:
                        print(f"   ❌ Não pode enviar mensagens: {e}")
                        continue
                
                return chat_id
                
            except Exception as e:
                print(f"   ❌ Não consegue acessar: {e}")
                continue
                
        except ValueError:
            print("   ❌ ID inválido! Use: -1001234567890 ou @nomedocanal")

async def get_mention_type():
    """Obtém o tipo de clonagem"""
    print("\n👤 TIPO DE CLONAGEM:")
    print("   1. Encaminhar (mantém autoria original)")
    print("   2. Copiar (envia como bot)")
    
    while True:
        choice = input("   👉 Escolha (1-2): ").strip()
        if choice in ['1', '2']:
            return int(choice)
        else:
            print("   ❌ Opção inválida!")

async def start_clone(app, clone_name, source_id, dest_id, mention_type):
    """Inicia uma nova clonagem"""
    print(f"\n🚀 INICIANDO CLONAGEM: {clone_name}")
    
    try:
        # Coleta informações dos canais
        source_chat = await app.get_chat(source_id)
        dest_chat = await app.get_chat(dest_id)
        
        print(f"📥 Origem: {source_chat.title}")
        print(f"📤 Destino: {dest_chat.title}")
        
        # Coleta mensagens
        print("\n📨 Coletando mensagens...")
        messages = []
        async for message in app.get_chat_history(source_id):
            messages.append(message)
        
        if not messages:
            print("❌ Nenhuma mensagem encontrada!")
            return
        
        messages.reverse()  # Mais antigo primeiro
        total_messages = len(messages)
        print(f"✅ {total_messages} mensagens para clonar")
        
        # Processa mensagens
        processed = 0
        for i, message in enumerate(messages, 1):
            print(f"\n[{i}/{total_messages}] Processando mensagem {message.id}...")
            
            try:
                success = await send_message(app, message, dest_id, mention_type)
                if success:
                    processed += 1
                    # SALVA PROGRESSO A CADA 10 MENSAGENS
                    if i % 10 == 0 or i == total_messages:
                        save_progress(clone_name, str(source_id), str(dest_id), message.id, total_messages, processed)
                        print(f"💾 Progresso salvo: {processed}/{total_messages}")
                
                await asyncio.sleep(0.5)  # Delay anti-flood
                
            except FloodWait as e:
                print(f"⏳ FloodWait: {e.value}s...")
                await asyncio.sleep(e.value)
                # Tenta novamente após wait
                try:
                    success = await send_message(app, message, dest_id, mention_type)
                    if success:
                        processed += 1
                        save_progress(clone_name, str(source_id), str(dest_id), message.id, total_messages, processed)
                except Exception as retry_error:
                    print(f"❌ Erro no retry: {retry_error}")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # Marca como concluído
        mark_clone_completed(clone_name)
        print(f"\n🎉 CLONAGEM CONCLUÍDA: {clone_name}")
        print(f"📊 Total: {processed}/{total_messages} mensagens")
        
    except Exception as e:
        print(f"❌ Erro na clonagem: {e}")

async def continue_clone(app, clone_name, progress_data):
    """Continua uma clonagem existente"""
    print(f"\n🔄 CONTINUANDO CLONAGEM: {clone_name}")
    
    source_id = progress_data['source_channel']
    dest_id = progress_data['destination_channel']
    last_msg_id = progress_data['last_message_id']
    total_messages = progress_data['total_messages']
    processed_before = progress_data['processed_messages']
    
    print(f"📊 Progresso anterior: {processed_before}/{total_messages}")
    print(f"📨 Última mensagem: {last_msg_id}")
    
    try:
        # Coleta mensagens novamente
        messages = []
        async for message in app.get_chat_history(source_id):
            messages.append(message)
        
        messages.reverse()
        
        # Encontra onde parou
        start_index = 0
        for i, msg in enumerate(messages):
            if msg.id == last_msg_id:
                start_index = i + 1  # Começa da próxima mensagem
                break
        
        messages_to_process = messages[start_index:]
        remaining = len(messages_to_process)
        
        print(f"🔄 Restam {remaining} mensagens")
        
        if not messages_to_process:
            print("✅ Nada para continuar - clonagem já está completa!")
            mark_clone_completed(clone_name)
            return
        
        # Processa mensagens restantes
        processed = processed_before
        for i, message in enumerate(messages_to_process, 1):
            print(f"\n[{processed + 1}/{total_messages}] Continuando mensagem {message.id}...")
            
            try:
                success = await send_message(app, message, dest_id, 2)  # Sempre copia ao continuar
                if success:
                    processed += 1
                    # Salva progresso
                    if i % 10 == 0 or i == remaining:
                        save_progress(clone_name, source_id, dest_id, message.id, total_messages, processed)
                        print(f"💾 Progresso salvo: {processed}/{total_messages}")
                
                await asyncio.sleep(0.5)
                
            except FloodWait as e:
                print(f"⏳ FloodWait: {e.value}s...")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # Marca como concluído
        mark_clone_completed(clone_name)
        print(f"\n🎉 CLONAGEM CONCLUÍDA: {clone_name}")
        print(f"📊 Total final: {processed}/{total_messages} mensagens")
        
    except Exception as e:
        print(f"❌ Erro ao continuar: {e}")

async def send_message(app, message, dest_id, mention_type):
    """Envia uma mensagem"""
    try:
        caption = message.caption or ""
        
        if mention_type == 1:
            # Encaminhar
            await message.forward(dest_id)
        else:
            # Copiar
            if message.text:
                await app.send_message(dest_id, message.text)
            elif message.photo:
                await app.send_photo(dest_id, message.photo.file_id, caption=caption)
            elif message.video:
                await app.send_video(dest_id, message.video.file_id, caption=caption)
            elif message.document:
                await app.send_document(dest_id, message.document.file_id, caption=caption)
            elif message.audio:
                await app.send_audio(dest_id, message.audio.file_id, caption=caption)
            elif message.sticker:
                await app.send_sticker(dest_id, message.sticker.file_id)
            else:
                print("⚠️  Tipo não suportado")
                return False
        
        return True
        
    except Exception as e:
        print(f"🔄 Método alternativo...")
        return await resend_media(app, message, dest_id, caption)

async def resend_media(app, message, dest_id, caption):
    """Reenvia mídia baixando"""
    path = None
    try:
        if message.photo:
            path = await message.download()
            await app.send_photo(dest_id, path, caption=caption)
        elif message.video:
            path = await message.download()
            await app.send_video(dest_id, path, caption=caption)
        elif message.document:
            path = await message.download()
            await app.send_document(dest_id, path, caption=caption)
        else:
            return False
        return True
    except Exception as e:
        print(f"❌ Erro alternativo: {e}")
        return False
    finally:
        if path and os.path.exists(path):
            os.remove(path)

async def manage_clones():
    """Gerencia clonagens salvas"""
    clones = list_saved_clones()
    
    if not clones:
        print("\n❌ Nenhuma clonagem salva encontrada!")
        return None
    
    print(f"\n📁 CLONAGENS SALVAS ({len(clones)}):")
    print("-" * 60)
    
    for i, clone in enumerate(clones, 1):
        status_icon = "✅" if clone['status'] == 'completed' else "🔄"
        print(f"{i}. {status_icon} {clone['name']}")
        print(f"   📊 {clone['processed']}/{clone['total']} mensagens")
        print(f"   📅 {clone['last_update'][:10]}")
        print(f"   🔗 Origem: {clone['source']} → Destino: {clone['dest']}")
        print()
    
    while True:
        try:
            choice = input("👉 Número da clonagem para continuar (0 para cancelar): ").strip()
            if choice == '0':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(clones):
                return clones[choice_num - 1]['name']
            else:
                print(f"❌ Escolha entre 1 e {len(clones)}")
        except ValueError:
            print("❌ Digite um número válido")

async def main_async():
    # Configuração inicial
    if not config_exists():
        print("\n=== CONFIGURAÇÃO INICIAL ===")
        api_id = input("🔑 API ID: ").strip()
        api_hash = input("🔑 API Hash: ").strip()
        save_api_credentials(api_id, api_hash)
        print("✅ Credenciais salvas!")
    
    api_id, api_hash = get_api_credentials()
    
    print("\n" + "="*50)
    print("🤖 TELEGRAM CHANNEL CLONER + SAVE SYSTEM")
    print("="*50)
    
    async with Client(SESSION_FILE_FMT, api_id=api_id, api_hash=api_hash) as app:
        print("✅ Conectado ao Telegram!")
        
        while True:
            print("\n" + "="*40)
            print("💾 SISTEMA COM SALVAMENTO")
            print("="*40)
            print("1. 🆕 Nova Clonagem")
            print("2. 🔄 Continuar Clonagem")
            print("3. 📊 Ver Clonagens Salvas")
            print("4. 🔍 Verificar Chats")
            print("5. ❌ Sair")
            print("-" * 40)
            
            choice = input("👉 Escolha (1-5): ").strip()
            
            if choice == '1':
                await manual_mode(app)
            elif choice == '2':
                clone_name = await manage_clones()
                if clone_name:
                    progress = load_progress(clone_name)
                    if progress:
                        await continue_clone(app, clone_name, progress)
            elif choice == '3':
                clones = list_saved_clones()
                if clones:
                    print(f"\n📁 Total de clonagens salvas: {len(clones)}")
                else:
                    print("\n❌ Nenhuma clonagem salva")
            elif choice == '4':
                chats = await debug_chats(app)
                if chats:
                    print(f"\n💡 {len(chats)} chats disponíveis")
            elif choice == '5':
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida!")

def main():
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n👋 Programa interrompido")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()