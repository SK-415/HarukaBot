<template>
  <div class="qq-chat">
    <v-app>
      <v-main>
        <v-card class="elevation-6">
          <v-toolbar color="red lighten-3" dark dense flat>
            <v-row no-gutters>
              <v-col>
                <v-row no-gutters justify="space-between">
                  <v-col cols="auto">
                    <v-icon small>fa-chevron-left</v-icon>
                  </v-col>
                  <v-col cols="auto">
                    <h3>🔥</h3>
                  </v-col>
                </v-row>
              </v-col>
              <v-col cols="auto">
                <h3 class="white--text">HarukaBot</h3>
              </v-col>
              <v-col class="text-right">
                <v-icon small>fa-user</v-icon>
              </v-col>
            </v-row>
          </v-toolbar>
          <v-container fluid ref="chat" class="chat chat-bg">
            <template v-for="(item, index) in messages">
              <v-row
                v-if="item.position === 'right'"
                justify="end"
                :key="index"
                class="message"
              >
                <div
                  class="message-box"
                  v-html="
                    item.msg.replace(/\n/g, '<br/>').replace(/ /g, '&nbsp;')
                  "
                ></div>
                <v-avatar color="deep-orange lighten-3" size="36">
                  <v-icon small>fa-user</v-icon>
                </v-avatar>
              </v-row>
              <v-row
                v-else-if="item.position === 'left'"
                justify="start"
                :key="index"
                class="message"
              >
                <v-avatar color="transparent" size="36">
                  <v-img src="/logo.png"></v-img>
                </v-avatar>
                <div
                  class="message-box"
                  v-html="
                    item.msg.replace(/\n/g, '<br/>')
                  "
                ></div>
              </v-row>
              <v-row
                v-else
                justify="center"
                :key="index"
                class="notify mt-1"
              >
                <div class="notify-box">
                  <span style="display: inline; white-space: nowrap">
                    <v-icon x-small color="blue" left>fa-info-circle</v-icon>
                  </span>
                  <span
                    v-html="
                      item.msg.replace(/\n/g, '<br/>').replace(/ /g, '&nbsp;')
                    "
                  ></span>
                </div>
              </v-row>
            </template>
          </v-container>
        </v-card>
      </v-main>
    </v-app>
  </div>
</template>

<script>
export default {
  name: "Messenger",
  props: {
    messages: {
      type: Array,
      default: () => []
    }
  }
};
</script>

<style scoped>
.chat {
  min-height: 150px;
  overflow-x: hidden;
}
.chat-bg {
  background-color: #f3f6f9;
  width: auto;
}
.message {
  position: relative;
  margin: 0;
}
.message .message-box {
  position: relative;
  width: fit-content;
  max-width: 55%;
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
  margin: 0.4rem 0.8rem;
  background-color: #fff;
}
.message .message-box::after {
  content: "";
  position: absolute;
  right: 100%;
  top: 0;
  width: 8px;
  height: 12px;
  color: #fff;
  border: 0 solid transparent;
  border-bottom: 7px solid;
  border-radius: 0 0 0 8px;
}
.message.justify-end .message-box::after {
  left: 100%;
  right: auto;
  border-radius: 0 0 8px 0;
}
.notify {
  position: relative;
}
.notify .notify-box {
  max-width: 70%;
  background: #e0e0e0;
  border-radius: 10px;
  padding: 5px 12px;
  font-size: 12px;
}
</style>

<style>
.v-application--wrap {
  min-height: 0 !important;
}
</style>