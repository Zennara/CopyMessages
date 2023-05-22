# CopyMessages
A simple bot used to copy and paste message history between channels. It can also work copying messages from server to server; however the bot must be in both servers.

### [Invite the Bot](https://discord.com/api/oauth2/authorize?client_id=1094873646943703071&permissions=533113166912&scope=applications.commands%20bot)

## Supported Messages
- ### System Messages
  - Join messages
  - Boost messages
  - Achieve new boost status
  - Pin messages
 
![image](https://github.com/Zennara/CopyMessages/assets/64995253/686c4a7a-cc49-44d2-89d3-a86dcd063f76)
![image](https://github.com/Zennara/CopyMessages/assets/64995253/e139f87b-cc32-4c5c-9372-09e406e37662)

- ### Author avatars and names
![image](https://github.com/Zennara/CopyMessages/assets/64995253/6de43669-8ea6-4967-b473-dd7282798735)


- ### Attachments over 25mb
  - If the attachment is over 25mb, it will simply append the link to the end of the message.
- ### Images, attachments, files

## Things that Won't Work
- thread creations (planned)
- views (can not implement)
- other system messages (planned)


# Usage
## Slash Commands
| Command  | Description                                | Arguments                                   |
|----------|--------------------------------------------|---------------------------------------------|
| `/copy`  | Copies the current channel.                |                                             |
| `/paste` | Pastes message history from copied channel | `start_at`: the message number to start at |

## Context Menu Commands
### Message
| Command | Description                                                           |
|---------|-----------------------------------------------------------------------|
| Message | Gets the clicked message's message number. Can be used in `start_for` |
