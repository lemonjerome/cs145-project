import { defineStore } from 'pinia';

export const useStoplightsStore = defineStore('stoplights', {
  state: () => ({
    stoplightGroups: [],
    stoplights: [],
  }),
  actions: {
    setStoplightGroups(groups) {
      this.stoplightGroups = groups;
    },
    setStoplights(stoplights) {
      this.stoplights = stoplights;
    },
    clear() {
      this.stoplightGroups = [];
      this.stoplights = [];
    }
  }
});